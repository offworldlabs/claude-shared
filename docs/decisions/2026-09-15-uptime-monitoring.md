# Uptime monitoring for the server droplets

- **Date:** 2026-09-15. **Status:** proposed; accepted when this merges.
- **Scope:** the first of three monitoring sub-projects for the server side. This one is
  outside-in uptime and host health. The second, making the in-process alerting trustworthy, is
  the set of open tickets on the ClickUp Alerts list. The third, metrics history and error
  tracking, is the 2026-08-17 design (VictoriaMetrics, Grafana, Sentry) and is not yet ticketed.
- **Ticket:** ClickUp `123zgec2z7a`. **Companion:** `../runbooks/uptime-monitoring.md`, written
  with the implementation, holds the commands and the expected end state.

## 1. What exists and what does not

retina-server evaluates thirteen health conditions every 30 s in-process and posts each to a
ClickUp chat channel over a webhook (`docs/alerting.md` in that repo). Docker healthchecks probe
both services every 30 s. The DigitalOcean metrics agent runs on the droplets. That is the whole
of it.

Nothing polls the public hostnames from outside. The heartbeat task that `docs/alerting.md`
describes as the dead-man's switch has never had `HEARTBEAT_URL` set on any droplet, so it has
never pinged anything. tower-finder-service has a health endpoint and no alerting. Staging's
webhook has no destination, so it alerts nobody. Cloudflare's Health Checks product is not
available on the Free plan the `retina.fm` zone is on. A droplet that is off, an nginx that has
stopped, or a Cloudflare-to-origin path that has broken is invisible until someone looks.

## 2. Decision

Watch from outside with the platforms already in use, alert by email, run nothing, and record
the configuration in a runbook so it can be re-applied and audited from the repository.

Four things, none of them application code except the dashboard page in §6:

| | What | Cost |
|---|---|---|
| Active probes | DigitalOcean Uptime, one check per ingress stack per environment (§3) | $3/month |
| Host health | DigitalOcean resource alert policies on every RETINA droplet (§4) | free |
| Edge and certificates | Two Cloudflare notification policies (§5) | free |
| Seeing it | DigitalOcean's own pages first, then a page in the admin dashboard (§6) | free |

Email is the only channel. The existing ClickUp channels carry the in-process alerts, whose
noise is the second sub-project's problem; an outage notice should not land in a stream that is
not yet trusted. Slack and Discord are not in use.

## 3. Active probes: one per ingress stack

Each environment has exactly two ways in. retina-server's nginx on 443 serves every hostname
except `towers`; the tower-finder edge on 8443 serves `towers`, because a Cloudflare origin rule
routes that hostname to the other port. Every other prod hostname (`map`, `dash`, `data`,
`admin`) is the same nginx and the same backend under a different name, so probing them
separately would count one failure four times.

| Check | Target | Alert |
|---|---|---|
| retina-server prod | `https://api.retina.fm/api/health` | `down_global`, 2 min |
| tower-finder prod | `https://towers.retina.fm/api/health` | `down_global`, 2 min |
| retina-server staging | `https://staging-api.retina.fm/api/health` | `down_global`, 2 min |
| tower-finder staging | `https://staging-towers.retina.fm/api/health` | `down_global`, 2 min |

Checks are HTTPS from all four regions (`us_east`, `us_west`, `eu_west`, `se_asia`) at the fixed
one-minute interval. `down_global` fires when every region has failed for the period, so a
regional network blip does not page and an origin outage, which every region sees, does. Each
check costs $1/month and the account gets one free.

`/api/health`, not `/api/health?strict=1`. The strict form returns 503 on any degraded
condition, including the warnings that are currently noisy; until those are calibrated it would
page on the operating point. Liveness is what an outside probe should assert.

Staging is included because production deploys are gated on staging passing its smoke tests: a
dark staging silently stops prod shipping. The test droplet is deployed on demand and is
excluded. `admin.*` sits behind Cloudflare Access and answers a probe with a 302; it shares its
backend with `dash`, so nothing is lost by leaving it out.

Latency and SSL-expiry alerts on the checks are not enabled. The certificate a probe sees is
Cloudflare's edge certificate, which Cloudflare renews and §5 covers; the origin certificate
expiring shows as a 526 and trips the down check. Latency has no calibrated threshold yet and
would only add noise.

## 4. Host health: resource policies by tag

Free, opt-in, and already possible because the metrics agent is installed. Policies target the
tag `retina` rather than named droplets, so a rebuilt or new droplet joins by being tagged.

| Metric | Fires when | Window |
|---|---|---|
| Disk utilisation | above 85 % | 5 min |
| Memory utilisation | above 90 % | 10 min |
| CPU | above 95 % | 1 h |

Disk is the one that has actually hurt: `docs/alerting.md` names the disk-full deploy
death-spiral as a failure mode in its own right. Memory is measured on the box, not the
container, so it catches the app and the fleet simulator together. CPU is deliberately blunt:
the solver is CPU-bound and staging's fleet keeps its box busy by design, so a high threshold
over a long window reports a box that is pinned rather than one that is working.

Tagged: `retina-prod`, `retina-staging`, `retina-test`, `Mender-Infra` and `adsb-prod`, every
droplet in the team. The thresholds are a starting calibration; the runbook records the values
in force.

## 5. Cloudflare notifications

Two account-level policies, both available on the Free plan, both to email:

- **Passive Origin Monitoring**: Cloudflare could not reach an origin for traffic it was
  carrying. Passive, so it needs traffic, which prod's node heartbeats supply every minute.
- **Universal SSL**: issuance, renewal and expiry events for the edge certificate.

## 6. Seeing it

**First, the pages that exist.** The DigitalOcean Uptime page lists every check with its
status; each check's page shows 30-day global uptime, the last outage and its duration,
per-region status and a latency graph over a selectable window. Each droplet's Monitoring tab
graphs CPU, memory, disk, bandwidth and load. The runbook links all of them. This costs nothing,
and it is where the alert emails point.

**Second, the same data in the admin dashboard.** The dashboard app already has System Metrics,
Network Health and Alerts pages behind Cloudflare Access. An Infrastructure page beside them
reads the DigitalOcean API through a new backend route: per check, regional status, 30-day
uptime and last outage; per droplet, current CPU, memory and disk with a 24-hour series. It
needs a DigitalOcean token with read-only scopes (`uptime:read`, `monitoring:read`,
`droplet:read`) in `backend/.env`, and the route caches the answer for a minute so the page
cannot exhaust the API. When the token is absent the page says so rather than rendering blanks,
and `backend/.env.example` documents the key. Nothing at deploy time asserts a `backend/.env`
key today; that is `86cb8cf0n`'s proposal and this page inherits whatever it lands.

This is a view, never the source: the alerts come from DigitalOcean and Cloudflare whether or
not the page loads. Its limit is the failure domain. `admin.retina.fm` is served by the prod
droplet, so during a prod outage the page to read is `staging-admin`, which shows the same
account-wide data. A single pane that survives everything is the third sub-project's problem.

## 7. Recording it

The configuration lives in the DigitalOcean and Cloudflare accounts, which a droplet rebuild
does not touch. What a rebuild does lose is the `retina` tag on the droplet, so re-tagging is a
step in the droplet setup runbook.

`docs/runbooks/uptime-monitoring.md` holds the table of what is configured, the `doctl` and API
commands that create each item, the commands that list the current state for an audit, the links
from §6, and how to add a hostname or a droplet. There is no reconciliation script: four checks,
three policies and two notifications change a few times a year, and the listing commands are the
audit. Revisit if that stops being true.

retina-server's `docs/alerting.md` currently proposes Healthchecks.io and UptimeRobot as
optional extras. It changes to point at the runbook. The heartbeat task stays as it is, dormant,
and nothing is documented as setting `HEARTBEAT_URL`.

## 8. Not done, and why

- **No heartbeat service.** With an outside-in probe, a dead-man's switch adds only the case
  where the in-process alert loop has died while HTTP still serves, and that loop catches its own
  exceptions each cycle. The case a heartbeat is the right tool for is the Mender auto-accept
  timer on `mender-infra`, which enrols new nodes every 30 s and has no HTTP surface. If it is to
  be watched, a ping from its systemd unit to a Healthchecks.io check is the whole job, and that
  is its own decision.
- **No page probes.** A status probe cannot tell a blank page from a working one; the deploy
  smoke tests exist for that.
- **No probe on `testmap`, `map`, `dash`, `data`, `admin` or any `test-*` name.** §3.
- **No Slack.** No workspace is in use.
- **No uptime check on `adsb.retina.fm`.** It is `adsb-prod`, a droplet in the same DigitalOcean
  team, so it carries the `retina` tag and the resource alerts; a check waits on knowing its
  health endpoint.

## 9. Prerequisites

- Access to the DigitalOcean team that owns the droplets, and a personal `doctl` token with
  write scope for uptime, monitoring and droplet tags, held by the operator and never in a
  repository.
- A second token with the read-only scopes in §6 for the dashboard page, placed in each
  droplet's `backend/.env` by hand, the same way the alerting secrets are.
- The email recipients. Al to begin with; DigitalOcean allows nine addresses per alert.

## 10. Acceptance

1. Stopping the staging `server` container produces a down email within about three minutes and
   a recovery email after it restarts. The same for `tower-finder-edge-staging`.
2. `doctl monitoring alert list` shows the three policies, each targeting the `retina` tag, and
   the five droplets carry it.
3. The two Cloudflare policies exist with the email destination verified.
4. The runbook exists and its listing commands reproduce the tables above.
5. `docs/alerting.md` in retina-server no longer tells a reader to set up a third-party monitor.
6. The Infrastructure page renders the four checks and four droplets on `staging-admin` and
   `admin`, and renders a clear "not configured" state when the token is removed.

## 11. Follow-ups

- Second sub-project: `86cb8cf0n`, `86cb87v86`, `86cb81jpp`, `86cb88z3y`, `86cb81gkn`,
  `86cb5c8dq`.
- Third sub-project: the 2026-08-17 metrics-and-errors design needs a ticket and a re-check of
  its premises; staging is no longer the 4 GB box it deferred.
- Heartbeat for the Mender auto-accept timer (§8).
- An uptime check for `adsb.retina.fm` (§8).
