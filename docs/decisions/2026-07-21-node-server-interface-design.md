# Node ↔ Server Interface Design

- **Date:** 2026-07-21; revised 2026-07-23 after priorities were refined, an ADS-B
  prior-art survey (§10) and on-node measurements.
- **Status:** Proposed (design agreed in discussion; implementation not started)
- **Scope:** How RETINA radar nodes communicate with the central server, phased: phase 1
  delivers live detections from up to ~50 nodes over HTTPS; the archive/bulk plane and the
  MQTT broker are future work, with their designs retained here so phase 1 does not
  foreclose them.
- **Supersedes (on cut-over):** the raw TCP `:3012` JSONL ingest (HELLO→CONFIG→DETECTION)
  currently spoken by nodes and `retina-simulation`.

## 1. Problem and priorities

Nodes are passive radar receivers (Raspberry Pi 5, 2 GB RAM, 64 GB SD card as the only disk)
on arbitrary consumer internet connections: slow, unreliable, behind NAT or CGNAT, and only
able to initiate connections outwards. The SD card is the wear item, so writes are minimised
and RAM preferred; the current radar workload fits comfortably in 2 GB, with one caveat
recorded in §2.3.

Priorities as of 2026-07-22:

1. **Live data from node to server**: a snapshot of current detections at 1–2 Hz, plus small
   control messages (pairing, account linking, config sync) and a low-rate command path back
   to the node.
2. **Archive and bulk transfer later**: the hourly snapshot archive and large capture
   uploads (IQ or Doppler map, §2.3) are future work.

The fleet stays at or below ~50 nodes in the near term, with thousands the eventual target.
We require mutual authentication, encryption (D15) and tolerance of poor links. The spike
that shaped the original design (many simultaneous capture uploads during a big event) moves
out with the bulk plane.

## 2. Design overview: three planes, phased

The traffic falls into three classes with different shapes, kept on separate planes with
independent failure modes.

| Plane | Carries | Phase 1 transport | At scale |
|---|---|---|---|
| **Live** | 1–2 Hz snapshots up; commands down | HTTPS POST, commands piggybacked on responses | Managed MQTT when a §2.2 tripwire fires |
| **Bulk/archive** | Capture files; hourly archive | Future work | HTTPS presigned upload direct to Cloudflare R2 |
| **Control/identity** | Pairing, account linking, config reporting | HTTPS (FastAPI on the droplet, via Cloudflare) | Unchanged |

```
   node ──HTTPS POST 1–2 Hz──► droplet FastAPI (ingest)            [via Cloudflare]
        ◄── commands + config version ride each response
   node ──HTTPS──────────────► droplet FastAPI (pairing, config)   [via Cloudflare]
   node ──HTTPS PUT──────────► Cloudflare R2 (bulk plane, future work)
```

### 2.1 Live plane, phase 1: HTTPS

- Each node POSTs its current snapshot at 1–2 Hz to the FastAPI ingest over a kept-alive TLS
  connection. At 50 nodes that is ~100 small requests/s, well within one droplet.
- Latest-wins (D3): the node keeps one request in flight and never queues; while a POST is
  slow, newer frames replace the pending one, and a request that exceeds its timeout (a few
  seconds) is abandoned, the next frame going in a fresh request. The live tracker cannot
  use stale detections (the multi-node association window in `retina-analytics` is 4 s).
- The downlink piggybacks on the uplink: each response carries any pending commands. While
  the radar runs this is sub-second push with no extra machinery; an idle node makes the
  same request without a frame every 30–60 s, so liveness and command delivery share one
  path. This is the PiAware adept pattern (§10): commands ride the node's own outbound
  channel.
- Config flows up, not down, in phase 1: the node reports its effective config to the
  server (a config hash with every telemetry message; the full merged config at startup
  and on change). The repeated hash costs a few bytes and makes the scheme self-healing: a
  purely event-driven report would leave the server silently stale if the one change event
  were lost. Server-side config distribution may come later with autoconfig, which may in
  any case stay node-local.
- Command delivery is at-least-once: commands carry IDs, the server repeats pending
  commands in every response until a later request acknowledges the last processed ID, and
  handlers are idempotent or guarded by that ID. A response can be lost after the server
  sends it, so transmission is never treated as delivery.
- Commands are a small fixed enum, gated by node-local allow flags so an owner can veto
  categories (§10). Software and OS updates are not commands: they stay pull-based via the
  existing Mender flow (A6); at most a command nudges an immediate Mender check-in.
- The working payload is detection frames, as today (tracks are a server-side product of
  `retina-tracker`); whether tracks replace or join them is open (§11).
- Liveness: the snapshot stream is its own heartbeat. A node silent for ~10 s (10–20
  missed snapshots) is marked offline; an idle-but-healthy node (radar stopped, slow poll
  active) is distinguished by its polls and telemetry, and marked offline after missing
  two slow polls (~2 minutes). This replaces the retained broker design's keepalive and
  last-will (§2.2).
- A health telemetry message (CPU, temperature, disk, uptime) rides the same path every
  ~5 minutes (§10).
- The ingest rate-limits per node credential (a small multiple of 2 Hz), and this is the
  isolating control: Cloudflare rate rules key on client IP, and under CGNAT (A2) one IP
  can be many nodes, so edge rules are tuned only for gross volumetric abuse. Ingest also
  applies cheap plausibility gates (impossible delay, Doppler or position values, §10)
  before frames reach the tracker.
- Payloads carry the existing `retina-custody` per-packet ECDSA signatures unchanged.
  Transport auth and data authenticity remain separate layers.

### 2.2 The broker: deferred, with return tripwires

The original design put the live plane on managed MQTT. Its sole hard requirement was
seconds-level push for capture requests racing the ring buffer, which leaves with the bulk
plane; the piggybacked downlink covers everything that remains, and no ADS-B network uses a
broker at any scale (§10). The broker is therefore deferred. Any of these reopens it:

1. The fleet approaching the high hundreds, where per-request overhead and connection count
   start to dominate (the scaling dimension, §3).
2. The bulk plane returning with a need to push to idle, non-snapshotting nodes faster than
   the slow poll allows.
3. Any other need for sub-second push to a node that is not currently snapshotting.

An intermediate step, still brokerless, is one long-lived HTTPS/SSE stream per node. D14
keeps the frame schema transport-neutral so the swap, whenever it happens, touches transport
code only.

Broker design retained for that day: QoS 0 uplink with a depth-1 publish queue on the node
(QoS 0 alone queues stale frames in order over a slow TCP link); QoS 1 downlink over
persistent sessions (`clean_start=false`) with MQTT 5 message expiry no longer than the ring
buffer and a payload timestamp checked node-side; keepalive plus last-will for liveness;
MQTT 5 shared subscriptions (`$share/ingest/...`) for droplet scale-out; per-node broker
credentials subordinate to the custody key (§2.4). Vendor notes in §6.

### 2.3 Bulk/archive plane (future work, design retained)

**Core invariant: the node writes every frame to local storage at capture time, before and
independently of any network send** (D4), so archive completeness never depends on what the
live channel delivered. Retained design: the spool compacts into one compressed file per
hour, aligned with the `retina-custody` hourly hash-chain segments; upload is a presigned
PUT direct to R2 keyed `(node_id, hour)` (S3 multipart for large captures: a URL per part
plus a completion call); a server-side completeness monitor over the key space alerts on
gaps, since a node can keep snapshotting while its upload path is broken; uploads are
rate-shaped below the node's uplink so a capture in flight does not starve the live plane or
the node's apparent liveness; write-once objects and contested-hour adjudication per D13.

Today's IQ path, for context: blah2 holds ~1.5 s of IQ in RAM (`process.data.buffer`),
consumes it in 0.5 s CPIs through clutter filtering, the ambiguity map and CFAR into
detections and its own tracker, and discards it; measured on a live node the whole
pipeline runs at ~760 MB RSS. The only raw capture that exists is blah2's `saveIq` toggle
(polled from its API once a second), which streams IQ forward to the SD card at ~8 MB/s
until switched off: no retrospective window, and unbounded SD writes while on (§11). The
retina-custody 120 s ring buffer is not deployed.

Two constraints recorded now so the future design starts from them:

- **SD write pattern.** The archive's daily volume is trivial (~11 MB compressed) but
  continuous small appends would wear the SD card far faster than volume suggests. The
  spool therefore accumulates each hour in RAM (~2 MB raw) and writes once per hour as the
  compacted file. Cost: a power loss drops up to an hour of archive; accepted. A live node
  shows no swap configured (§3); keep it that way, since owl-os sets nothing about swap
  and a future base image could reintroduce a swapfile, converting memory pressure into
  the same wear invisibly.
- **IQ versus Doppler map.** 120 s of real IQ is ~960 MB (§3) and does not fit in 2 GB
  alongside the OS and radar processing; `iq_buffer.py` defaults to synthetic 1 KB chunks
  and only `retina-simulation` instantiates the buffer, so the real path has never run on
  node hardware. The candidate replacement is the delay-Doppler map blah2 already computes
  each CPI (~650 kB as JSON, §3): a 120 s window is ~240 maps ≈ 156 MB as JSON, roughly 6×
  smaller than the IQ and considerably better once binary-encoded and compressed, and
  small enough that a rolling RAM buffer of maps fits in 2 GB. That restores the
  retrospective capture window this hardware cannot afford for raw IQ (and which the
  forward-only `saveIq` path lacks). Continuous map streaming is ruled out (2 Hz × 650 kB
  ≈ 10 Mbps, beyond consumer uplinks); map transfer means event-windowed capture over the
  bulk plane. The trade-off: a map cannot be re-processed with different parameters after
  the fact, and the raw-evidence forensic character of IQ is lost. The map is the working
  assumption; IQ returns only if analysis of real captured maps proves them insufficient
  (§6 item 4). blah2's forward-only `saveIq` toggle is excluded from the design either
  way: streaming ~8 MB/s to the SD card conflicts with the wear budget.

### 2.4 Control/identity plane

- Transactional, node-initiated operations run over HTTPS to the existing FastAPI backend,
  fronted by Cloudflare: pairing, account linking, config reporting. Request/response by
  nature, and they must work before any other credential exists.
- Pairing and bootstrap: the node generates (or already holds, via `retina-custody`) its
  P-256 keypair; the user enters a claim code in the retina-gui setup wizard; the server
  binds the node's public key to the account and provisions its API credential in
  whichever form §6 item 1 settles on. This parallels the Mender auto-accept flow that
  `node-infra` already runs; the PiAware claim UX is the usability benchmark (§10).
- The custody key is the root identity; transport credentials (API token now, broker
  credential later) are subordinate and replaceable through this plane. Revoking a node
  disables its credential and rejects its custody signature, with no effect on any other
  node.
- Mender as a config stopgap: the configure add-on is disabled on the current plan, so
  Mender cannot push config. It can track it: a custom inventory script reports the merged
  effective config (retina-node merges default/user/forced at deployment time) as device
  attributes, say a hash plus the load-bearing keys, and with the inventory poll interval
  shortened from its 8 h default to a few minutes the droplet polls Mender's device API
  for close-to-live visibility of what each node actually runs. The troubleshoot add-on
  (enabled) additionally allows on-demand pull of the actual config file from a connected
  device. Config push stays with deployments (A6). The inventory stopgap is interim: built
  now, retired once the §2.1 channel carries config reports at cut-over.
  The field list in the "Configuration Data on Server" ticket (ClickUp 86caq4a90) splits
  along this seam: owner identity and contact are entered at pairing and land in the cloud
  database; antenna, location and install details live in node config and suit inventory
  reporting. Low-sensitivity owner fields (display name, system name, town) also ride
  inventory, where troubleshooters working in the Mender UI benefit from them; contact
  details (email, phone) stay in the cloud database only.

## 3. Parameters (measured or derived; restate in code as config, not magic numbers)

| Parameter | Value | Source |
|---|---|---|
| Snapshot cadence | 1–2 Hz: one frame per CPI or every other; the 0.5 s CPI (`process.data.cpi`) sets detection and map cadence together | `blah2-arm/config/config.yml:24` |
| Snapshot frame size | ~276 B (9 detections, JSON) | measured from `radar3.retnode.com/api/detection`, 2026-07-21; unsigned payload, the custody envelope adds ~100 B, so derived volumes are floors (A7) |
| Raw snapshot volume | ~48 MB/day/node at 2 Hz | derived |
| Phase 1 ingest at 50 nodes | ~100 req/s, ~30 kB/s | derived |
| Fleet ingest at 5,000 nodes | ~3 MB/s aggregate; connection and request count is the scaling dimension, not bandwidth | derived |
| Node RAM | Mixed fleet: 8 of 11 sampled nodes at 2 GB, 3 at 4 GB; available RAM 575 MB min, 892 MB median, 2,485 MB max; blah2 ~760 MB RSS; no swap on any node | fleet probe via Mender terminal, 11 nodes, 2026-07-23 |
| IQ ring buffer | 120 s (`DEFAULT_BUFFER_DURATION_S`); ~960 MB real (120 s × 2 MHz × 2 ch × 2 B); code defaults to synthetic 1 KB chunks | `retina-custody/retina_custody/iq_buffer.py:36-40` |
| Delay-Doppler map size | ~650 kB (JSON) per map | measured from `radar3.retnode.com/api/map`, 2026-07-22 |
| Hourly archive compression | ~4.3× (gzip -9; zstd should do better) | measured on a synthetic hour |
| Archive volume | ~11 MB/day/node | derived |
| Node disk budget | Root fs 18 GB with ~16 GB free on the standard image (one 26 GB outlier); the Mender A/B layout implies a separate data partition, unmeasured; confirm its size before archive budgeting | fleet probe, 2026-07-23 |
| Command latency budget | ~1 s while snapshotting (piggyback); 30–60 s when idle (slow poll) | §2.1 |

Archive retention, capture caps and the eviction policy move out with the bulk plane;
re-derive them from §2.3's constraints (RAM-hourly spool, capture size) when it returns.

## 4. Decisions

- **D1, three separate planes.** Each plane stays simple and fails independently; modes in
  §7. The ADS-B ecosystem's split of light live feeds from raw/heavy side channels is the
  same shape (§10). Mender is in effect a pre-existing fourth plane (software and OS
  lifecycle, plus the §2.4 inventory stopgap); it stays out of scope here (A6) but shares
  the same independent-failure property.
- **D2, HTTPS for the live plane now; managed MQTT when a §2.2 tripwire fires.** The
  original broker choice rested on the seconds-level capture push, which left with the bulk
  plane. Alternatives for the eventual at-scale transport, considered and set aside:
  - *NATS + JetStream*: durable streams are unnecessary once the archive lives on the bulk
    plane (D4), and there is effectively one managed vendor.
  - *HTTPS-only at scale*: fine for telemetry, but sub-second push to idle nodes means
    either aggressive polling or a persistent stream, and a managed broker is the commodity
    form of the latter.
  - *gRPC or WebSocket streams to our own server*: we would own reconnect storms, sticky
    load balancing and backpressure, rebuilding a worse broker.
  - *Overlay network (WireGuard/Tailscale)*: solves auth, encryption and NAT but not
    queueing or burst semantics; an ops and debugging complement, not a data plane.
  Managed rather than self-hosted buys time for a small team; MQTT rather than NATS is the
  commodity choice with several vendors.
- **D3, latest-wins snapshots, transport-independent.** The node sends only the newest frame
  and never queues, whatever the transport (§2.1, §2.2).
- **D4, the archive is built from the local spool, never from live-channel delivery**
  (future work; invariant in §2.3). An archive assembled from live delivery would inherit
  its losses.
- **D5, bulk bytes go direct to R2 via presigned URLs** (future work, §2.3). The droplet
  never carries bulk bytes; R2 is already in use for the Tower-Finder archive and charges
  nothing for egress.
- **D6, hybrid loss semantics** (future work). The live plane is lossy and real-time only;
  the archive is eventually complete within its retention window for any node that
  reconnects. A node offline beyond retention, or an SD card that dies while offline, loses
  data; data on a recovered card remains signed and hash-chained, with the limits of that
  claim in D13.
- **D7, nodes are semi-trusted; no hardware attestation for now.** A stock Pi has no secure
  boot: someone with the SD card can extract the node key or modify the rootfs undetected,
  so authentication proves which node key sent the data, not that the data is true. Truth is
  enforced server-side by `retina-analytics` reputation (blocking at trust <0.1 or
  reputation <0.2), with per-node revocation for containment. The ADS-B survey reinforces
  this: mature networks trust cross-node corroboration, not node identity, and at ≤50 nodes
  the uncorroborated lone node is our common case, so per-node keys and trust scoring stay
  (§10). The ATECC608B secure element stubbed in `retina-custody` remains the upgrade path.
- **D8, protocols split by traffic shape.** In phase 1 every plane happens to speak HTTPS,
  but the planes stay distinct so transports can diverge again at scale.
- **D9, accept ~23% uplink duplication when the archive returns** (the compressed archive
  adds ~11 MB/day/node on top of the ~48 MB live feed). Gap-filling was rejected: per-frame
  bookkeeping on both sides and a two-source archive, against links where the whole feed
  averages 5.5 kbps.
- **D10, a clean cut-over is allowed.** No `:3012` compatibility requirement. Migration in
  §8; `retina-simulation` moves to the new protocol and doubles as the load-test rig.
- **D11, payload encoding stays an open choice** (§6). JSONL is acceptable initially;
  protobuf (4–5× smaller, typed) can come later without touching the architecture.
- **D12, nothing we run accepts unsolicited inbound.** The droplet is reached through a
  Cloudflare Tunnel (`cloudflared` connects outbound, so the origin needs no open inbound
  ports) with a DigitalOcean Cloud Firewall denying all inbound as backstop; this beats
  allow-listing Cloudflare's IP ranges, which leaves a public listener and a range list to
  keep in sync. Phase 1 has no broker endpoint at all; when one arrives, managed vendors
  carry the fleet's TCP with their own DDoS protection (a §6 vendor criterion), and the
  self-hosted contingency postures live with the vendor choice in §6. Two clarifications: a
  DO firewall only drops non-matching packets (no layer 7, no volumetric absorption), and
  mTLS only authenticates (it rejects strangers cheaply at the handshake and does nothing
  about volumetric floods).
- **D13, the archive is tamper-evident** (future work, design retained). At presign time the
  control plane checks for an existing `(node_id, hour)` object: matching checksum reports
  success without a URL; a differing checksum refuses and alerts. Idempotent retry survives
  and a compromised node key cannot rewrite uploaded history. Write-once establishes which
  upload came first, not which writer was genuine; adjudication of a contested hour rests on
  two anchors used together: the hash chain (`prev_hash` orphans a substituted hour once the
  genuine successor arrives) and a per-`(node_id, hour)` ingest fingerprint of frames seen
  on the live plane, checked by containment, never equality, since the live plane is lossy.
  Each covers the other's blind spot: the chain fork needs a successor, so it says little
  for a dead or held-offline node, where the fingerprint anchors; the fingerprint is empty
  for unwitnessed hours, where lineage from locked neighbours anchors. An attacker who
  preserves observed frames while fabricating the unobserved passes the fingerprint, so its
  value is against wholesale fabrication. None of this proves truth after full node takeover
  (D7); the aim is bounding tampering in time and making it evident rather than silent.
- **D14, the frame schema is transport-neutral.** The same signed detection frame travels as
  a POST body today and an MQTT payload later; transports may add envelopes but never touch
  the frame, so the D2 swap is transport code only. Schemas live in
  `claude-shared/docs/contracts/`.
- **D15, TLS everywhere, despite the ADS-B precedent.** Most feeder networks ship
  unencrypted (§10) because their underlying data is a public broadcast and the feed holds
  no secrets; the one encrypted channel in that ecosystem (PiAware's) is the one that
  carries commands. Ours carries commands and credentials from day one, and the custody
  story wants transport integrity, so everything runs over TLS.

## 5. Assumptions

- **A1** Nodes are Raspberry Pi 5 with the SD card as the only disk; the fleet is mixed,
  mostly 2 GB RAM with a 4 GB minority (§3), and new builds will mostly be 2 GB, so
  designs hold to the 2 GB floor. The radar
  keeps observing during internet outages. The current workload fits in 2 GB with roughly
  600 MB headroom and no swap (§3), so memory spikes meet the OOM killer rather than
  degrading gradually; the real 120 s IQ path has never been exercised on node hardware
  (§2.3).
- **A2** Any consumer connection type, including CGNAT; nodes initiate all connections and
  accept nothing inbound. This is the target posture, not the present one: today's nodes
  expose blah2's API publicly (per-node `retnode.com` hostnames), which §8 retires. The
  posture is also a customer requirement, not just hygiene avoidance: participants should
  not need to expose anything publicly to run a node.
- **A3** The event spike (simultaneous capture uploads) belongs to the bulk plane and moves
  out with it; the fixed snapshot rate does not spike.
- **A4** A single DO droplet today; horizontal expansion someday via the broker and more
  droplets (§2.2).
- **A5** The live pipeline never needs late data (the association-window rationale is in
  §2.1); retrospective analysis is a batch job over the future R2 archive.
- **A6** Mender/OTA and the existing custody signing scheme continue; this design adds
  transport and replaces neither. The only Mender-side change is the §2.4 inventory script
  and a shorter inventory poll.
- **A7** The ~276 B frames are representative; re-derive §3 if they change by an order of
  magnitude.
- **A8** (applies when the archive returns) Hour keying and chain segments require correct
  absolute time. Online, nodes are NTP-synced (multi-node association already assumes
  this). During an outage the node timestamps against the monotonic clock and rewrites to
  absolute time once resynced, before compaction; a reboot mid-outage loses that anchor
  unless the Pi 5's onboard RTC has its battery fitted, so fit the battery. The control
  plane sanity-checks claimed hours at presign time. If monotonic-only data does reach the
  server, upload-time anchoring still recovers exact absolute times provided the node has
  not rebooted since capture (the pair of monotonic-now and absolute-now converts every
  buffered offset); after a reboot the server can only bracket the data between the node's
  last online contact and the upload. Battery presence is confirmable only by a power
  cycle test (a battery-backed RTC reports sane time before NTP); RTC device presence and
  its offset are fleet-checkable via the §2.4 inventory script. RTC devices were present
  and correctly set on all 11 nodes sampled 2026-07-23; battery presence remains
  unconfirmed.

## 6. Open implementation choices (item 1 blocks §8 step 2; the rest are flagged, not blocking)

Phase 1:

1. **Control-plane and ingest authentication.** Requests signed with the custody key, or a
   bearer token issued at pairing. The ingest POST now, and presign issuance later, are the
   security chokepoints.
2. **Message schemas**: snapshot frame, command enum, config report and health telemetry
   in `claude-shared/docs/contracts/` before implementation (D14).
3. **Protobuf now or JSONL first** (D11). Tripwires for moving: adopting any
   traffic-metered broker plan (item 5), the fleet passing a few hundred nodes, or the
   schemas stabilising after phase 1; until one fires, JSONL stands.

Medium term:

4. **The map-sufficiency falsification test** (§2.3). The delay-Doppler map is assumed
   sufficient until proven otherwise; define which analyses would demand raw IQ, run them
   on real captured maps, and reopen IQ capture only if one fails. While the assumption
   holds, the bulk plane shrinks several-fold (more once binary-encoded) and the RAM
   constraint dissolves.

When the broker returns (§2.2):

5. **Managed MQTT vendor.** Evaluate on price at 1k/5k nodes, the per-node credential and
   ACL provisioning API, mTLS versus token auth (serverless tiers are often token-only),
   MQTT 5 shared-subscription, session-expiry and message-expiry support, documented DDoS
   mitigation and connection-rate limiting (D12), and region options. Cost snapshot as of
   July 2026, priced at 5,000 always-connected nodes, 2 Hz, ~276 B frames (~26 bn messages,
   ~7 TB/month):

   | Option | Pricing shape | At 6 nodes | At ~5k nodes |
   |---|---|---|---|
   | EMQX Cloud Serverless | Free to 1,000 connections, then pay as you go | Free | N/A (connection cap) |
   | EMQX Cloud Dedicated Flex | Single-tenant cluster, from ~$234/month, 99.99% SLA | Overkill | Low hundreds $/month plus traffic |
   | HiveMQ Cloud | Free to 100 connections; Starter ~$0.34/hr; Standard ~$1.50/hr to 10k devices | Free/Starter | ~$250 to $1,100/month |
   | AWS IoT Core | ~$1 per million messages | ~$30/month | **~$19k/month; ruled out.** Per-message pricing is the wrong shape for high-frequency telemetry |
   | Cloudflare | No MQTT product; Pub/Sub sunset 2025-08-20 | N/A | N/A |
   | Self-hosted (EMQX OSS or Mosquitto on a droplet) | $20 to 50/month droplet | Trivial | Capacity ample; the cost is ops: provisioning, TLS, monitoring, upgrades, reconnect storms, single point unless clustered (Mosquitto cannot cluster) |

   If self-hosting, the D12 exposure question reopens: a direct MQTT/TLS listener requiring
   mTLS at the handshake, on its own droplet and IP (never the API origin), accepting
   volumetric risk that D1 bounds to live-map degradation since 8883 must stay open to
   arbitrary consumer IPs; or MQTT over WebSocket on 443 through the normal Cloudflare proxy
   with the broker origin behind its own Tunnel, which buys Cloudflare's mitigation and a
   zero-inbound broker but terminates TLS at the edge, so per-node mTLS gives way to token
   auth (item 6). Per-node `cloudflared access tcp` tunnels would be an overlay network in
   effect and are set aside with the overlays in D2.
6. **Broker credential format**: mTLS client certs or broker-issued tokens, either way
   subordinate to and replaceable via the custody key (§2.4).

When the archive returns:

7. **Retention and cap parameters**, node side and R2 side (the R2 archive grows ~55 GB/day
   at 5,000 nodes; decide retention and who deletes captures after analysis).
8. **Upload-slot throttling**: start unthrottled, monitor R2 cost, ration presigned URLs if
   needed.
9. **D13 mechanics and timing**: fingerprint at ingest from day one or deferred; the
   checksum flow through the presign API. Tripwire: decide before the first bulk-plane
   implementation change, since the checksum flow must be in the presign API from its
   first version and retrofitting write-once touches node retry logic.

## 7. Failure modes (phase 1)

| Failure | Live map | Commands | Recovery |
|---|---|---|---|
| Node link down | Node's detections absent | Held server-side | Reconnect; latest-wins means no stale burst |
| Droplet outage | Fleet-wide: no ingest | None delivered (single point in phase 1) | Restore droplet; a broker would decouple this at scale (§2.2) |
| Cloudflare outage | Fleet-wide | None | Vendor's SLA; accepted as rare |
| Node key or credential compromised | Fake but authenticated data possible | Attacker can drain or suppress the node's pending commands until revocation | Reputation flags it; revoke the credential; contested archive hours (future) per D13 |

Broker and R2 rows return with their planes; the original analysis (jittered reconnect
backoff, spool-covers-outage, vendor SLA absorption) carries over unchanged.

## 8. Migration sketch (phase 1)

Precondition: the prod droplet was resized to 8 GB (July 2026), which removes the memory
pressure; a swapfile is still worth adding (ClickUp 86cau7hbg), and the map broadcast loop
remains compute-bound (86cau8uu2), so resolve or consciously accept the latter before
pointing fleet ingest at it.

1. Specify the transport-neutral frame schema and command enum in
   `claude-shared/docs/contracts/` (D14).
2. Add the HTTPS ingest and piggyback responses to FastAPI; the node publishes alongside the
   existing `:3012` forward (dual-run; Tower-Finder keeps reading only `:3012` until step 4,
   so the dual feed is never double-ingested).
3. Port `retina-simulation` to the new protocol; load-test 50–500 synthetic nodes against
   staging.
4. Switch Tower-Finder ingest to the FastAPI feed; retire the two legacy ingest paths,
   `:3012` (Tower-Finder's raw TCP JSONL listener that nodes push detections to) and
   `blah2_bridge` (the server-side poller that scrapes each node's public blah2 API), and
   with the bridge the nodes' public API exposure (the `retnode.com` hostnames), bringing
   reality in line with A2. Both paths are superseded by the §2.1 ingest, and the bridge
   is what forces the public exposure.
5. Cut the fleet over via a `retina-node` release (Mender OTA), six nodes first.

## 9. Testing (phase 1)

- **Load:** 500 synthetic nodes at the real 2 Hz cadence (retina-simulation's 0.5 s frame
  interval, not the 40 s interval the synthetic testmap fleet runs at) against staging;
  droplet CPU and p99 ingest latency.
- **Command latency:** p99 piggyback delivery against the ~1 s budget while snapshotting;
  slow-poll bound when idle.
- **Chaos:** kill node links mid-stream; verify latest-wins on reconnect (no stale burst)
  and clean re-authentication.
- **Security:** revoke a node mid-stream and verify ingest rejection; plausibility gates
  reject impossible detections (§10).

## 10. Prior art: ADS-B feeder networks (surveyed 2026-07-22)

The closest existing analogue in network shape: tens of thousands of hobbyist receivers on
consumer connections feeding central aggregators. Findings that shaped this revision:

- **Transport.** Every network uses node-initiated persistent outbound TCP with trivial
  fixed-delay reconnect, brokerless even at FlightAware's ~43k feeders (one TLS connection
  each). Only FlightAware encrypts (D15). Clients rate-limit before
  upload (readsb `beast_reduce`, at most one state update per aircraft per 125–250 ms), the
  same shape as our snapshots.
- **Push.** Only FlightAware pushes commands: a small fixed enum (update, restart, reboot)
  multiplexed down the node's own outbound connection, gated by node-local allow flags.
  PiAware also reports a receiver health message (clock, CPU temperature, load, disk,
  uptime) every 5 minutes on the same connection. Everyone else is pull-only (apt repos,
  container updates).
- **Identity.** Bearer tokens throughout: server-assigned UUIDs claimed into an account by
  a claim page (same-public-IP association or manual ID entry) at PiAware, emailed sharing
  keys (FR24), or self-generated UUIDs with no account at all (the readsb aggregators).
  Nothing cryptographic except the incentive-bearing newcomer Wingbits, which signs per
  device because token rewards invite fabrication. Our ECDSA scheme already exceeds the
  incumbents.
- **Trust.** Corroboration, not authentication: MLAT positions need 3–4+ clock-synchronised
  receivers, clock-sync residuals double as continuous per-receiver honesty scoring, and the
  academic detectability bound is three or more benign sensors observing the same airspace
  (NDSS 2021). FR24 delays new tracks until verified; OpenSky applies plausibility filters.
  ADS-B-equipped aircraft
  double as known-truth calibration targets, worth designing into cross-node timing.
- **Bulk.** No network uploads raw samples; the one raw-ish channel (MLAT timing data) runs
  on a separate transport from the live feed, which validates the plane split (D1).

Key sources: the piaware repository (adept client, `update.tcl`), the readsb README
(`beast_reduce`, net-connectors), mutability/mlat-server, the OpenSky IPSN 2014 paper,
"Trust the Crowd" (NDSS 2021), and the FR24 T-Feed manual.

## 11. Open questions

1. Tracks, detections, or both in the live payload. Josh favours node-side tracks (the
   detections are noisy, tracks are smaller, and the node needs no server round-trip). The
   case for detections staying primary: a lone bistatic node cannot geolocate, so its
   tracks live in delay-Doppler space and the server must still associate across nodes;
   track-to-track fusion is weaker than measurement-level fusion and needs covariances the
   tracks would have to carry; per-node tracks previously produced duplicated aircraft when
   never merged; cross-node corroboration and reputation (D7) consume measurements; and at
   ~276 B per frame there is no bandwidth worth saving. A middle path: detections annotated
   with node-local tracklet IDs, giving the server smoothing hints without losing the
   measurements. Unresolved.
2. Which analyses would demand raw IQ rather than the delay-Doppler map? The map is
   assumed sufficient (§2.3, §6 item 4); this question is the falsification list for that
   assumption.
3. How command execution results are reported. The §2.1 acknowledgement only proves the
   node *received* a command; execution can then fail (disk full, radar stopped), succeed
   slowly, or succeed invisibly (the effect lands elsewhere, such as a future capture
   appearing in R2, never in the response stream). The choice is between an explicit
   result message per command ID on the §2.1 uplink (simple, adds one message type, makes
   failures visible) and inference from side effects (no new message, but failures are
   silent and surface only as timeouts). Leaning: explicit results, since the command enum
   is small.
4. (When the archive returns) The spool source: snapshot frames or the underlying
   detection stream (§3 volumes assume frame rate), and what triggers a local capture, at
   what rate.
5. (When the broker returns) Confirm MQTT 5 session-expiry and message-expiry support
   (§2.2), and add an ingest timestamp check, since shared subscriptions can reorder a
   node's frames across droplets.
