# Runbook: uptime monitoring for the server droplets

What watches the droplets from outside, where to look, how to reproduce or audit the
configuration, and how to change it. The decision behind it is
[`../decisions/2026-09-15-uptime-monitoring.md`](../decisions/2026-09-15-uptime-monitoring.md).
Everything here is platform configuration held in the DigitalOcean and Cloudflare accounts;
nothing runs on the droplets for it.

## What is configured

| Layer | Item | Alert | Where it lives |
|---|---|---|---|
| Outside-in probe | Uptime check `retina-server prod`: `https://api.retina.fm/api/health` | `down_global`, 2 min, email | DigitalOcean, Uptime |
| Outside-in probe | Uptime check `tower-finder prod`: `https://towers.retina.fm/api/health` | `down_global`, 2 min, email | DigitalOcean, Uptime |
| Outside-in probe | Uptime check `retina-server staging`: `https://staging-api.retina.fm/api/health` | `down_global`, 2 min, email | DigitalOcean, Uptime |
| Outside-in probe | Uptime check `tower-finder staging`: `https://staging-towers.retina.fm/api/health` | `down_global`, 2 min, email | DigitalOcean, Uptime |
| Host health | Disk utilisation above 85 % for 5 min, tag `retina` | email | DigitalOcean, Monitoring |
| Host health | Memory utilisation above 90 % for 10 min, tag `retina` | email | DigitalOcean, Monitoring |
| Host health | CPU above 95 % for 1 h, tag `retina` | email | DigitalOcean, Monitoring |
| Edge | Passive Origin Monitoring for `retina.fm` | email | Cloudflare, Notifications |
| Edge | Universal SSL events for `retina.fm` | email | Cloudflare, Notifications |

Checks run every minute from `us_east`, `us_west`, `eu_west` and `se_asia`, and cost $1 per
check per month with one free. The tag `retina` is on all five droplets in the team:
`retina-prod`, `retina-staging`, `retina-test`, `Mender-Infra` and `adsb-prod` (the
`adsb.retina.fm` origin).

Why these four targets and not one per hostname: each environment has two ingress stacks,
retina-server's nginx on 443 and the tower-finder edge on 8443 (a Cloudflare origin rule
routes `towers` there). Every other hostname is one of those two under another name.

## Where to look

- **DigitalOcean, Uptime**: every check with its status. A check's own page shows 30-day
  global uptime, the last outage and its duration, per-region status and a latency graph.
- **DigitalOcean, Droplets, Monitoring tab**: CPU, memory, disk, bandwidth and load per
  droplet. Alert policies are under Monitoring, Alerts.
- **Cloudflare, Notifications**: the two policies and their delivery history.
- **The admin dashboard, Infrastructure page** (`admin.retina.fm`, or `staging-admin.retina.fm`
  when prod is the thing that is down): the same check states and droplet metrics behind the
  Cloudflare Access gate. It is a view; the alerts above fire whether or not it loads.

## Audit: is the configuration still what this page says?

```bash
doctl auth switch --context retina
doctl compute droplet list --tag-name retina --format ID,Name,PublicIPv4,Tags
doctl monitoring alert list --format UUID,Type,Compare,Value,Window,Tags,Enabled
doctl monitoring uptime list --format ID,Name,Type,Target,Regions,Enabled
for id in $(doctl monitoring uptime list --format ID --no-header); do
  doctl monitoring uptime alert list "$id" --format ID,Name,Type,Period
done
curl -sS -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/05ded1830623d1c9a3f0c60140d87e27/alerting/v3/policies" \
  | python3 -m json.tool | grep -E '"name"|"alert_type"|"enabled"'
```

Compare with the table above. Five droplets, three policies, four checks each with one
`down_global` alert, two Cloudflare policies plus the budget alert.

## Reproduce from nothing

Recipient first: `export ALERT_EMAIL=<an address on the DigitalOcean team>`.

```bash
# Tag (a rebuilt droplet is a new droplet and needs this again)
doctl compute tag create retina
doctl compute droplet tag <droplet-id> --tag-name retina

# Resource policies
doctl monitoring alert create --type v1/insights/droplet/disk_utilization_percent \
  --compare GreaterThan --value 85 --window 5m --tags retina --emails "$ALERT_EMAIL" \
  --description "RETINA droplet disk above 85% for 5 min"
doctl monitoring alert create --type v1/insights/droplet/memory_utilization_percent \
  --compare GreaterThan --value 90 --window 10m --tags retina --emails "$ALERT_EMAIL" \
  --description "RETINA droplet memory above 90% for 10 min"
doctl monitoring alert create --type v1/insights/droplet/cpu \
  --compare GreaterThan --value 95 --window 1h --tags retina --emails "$ALERT_EMAIL" \
  --description "RETINA droplet CPU above 95% for 1 h"

# Uptime checks, one per ingress stack per environment
id=$(doctl monitoring uptime create "retina-server prod" --type https \
  --target https://api.retina.fm/api/health --regions us_east,us_west,eu_west,se_asia \
  --enabled true --format ID --no-header)
# doctl insists on a comparison and threshold even for down_global; both are ignored.
doctl monitoring uptime alert create "$id" --name "retina-server prod down" \
  --type down_global --period 2m --comparison less_than --threshold 0 --emails "$ALERT_EMAIL"
# repeat for: "tower-finder prod" https://towers.retina.fm/api/health,
#             "retina-server staging" https://staging-api.retina.fm/api/health,
#             "tower-finder staging" https://staging-towers.retina.fm/api/health

# Cloudflare policies (account 05ded1830623d1c9a3f0c60140d87e27 owns retina.fm)
curl -sS -X POST -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/05ded1830623d1c9a3f0c60140d87e27/alerting/v3/policies" \
  --data "{\"name\":\"RETINA origin unreachable\",\"alert_type\":\"real_origin_monitoring\",\"enabled\":true,\"mechanisms\":{\"email\":[{\"id\":\"$ALERT_EMAIL\"}]},\"filters\":{}}"
curl -sS -X POST -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/05ded1830623d1c9a3f0c60140d87e27/alerting/v3/policies" \
  --data "{\"name\":\"RETINA edge certificate events\",\"alert_type\":\"universal_ssl_event_type\",\"enabled\":true,\"mechanisms\":{\"email\":[{\"id\":\"$ALERT_EMAIL\"}]},\"filters\":{}}"
```

## Prove an alert fires

Staging only, and say so in the team channel first: a merge to `main` during the window fails
its staging smoke test.

```bash
ssh retina-staging 'cd /opt/retina-server && docker compose stop server'   # down email in 2-4 min
ssh retina-staging 'cd /opt/retina-server && docker compose start server'  # recovery email follows
```

For the tower-finder edge use `/opt/tower-finder-service` and the service `edge`.

## Change it

- **A new public hostname** gets no check unless it is a new ingress stack (a new port or a
  new nginx). If it is, add one check and one alert as above and a row to the table.
- **A new or rebuilt droplet**: tag it `retina`; the three policies apply through the tag.
- **A threshold**: `doctl monitoring alert update <uuid> --value <n> --window <w>`; update the
  table in the same change.
- **The recipient**: DigitalOcean alerts accept up to nine addresses; Cloudflare policies take a
  list. Both must be addresses the platform knows.

## Not covered, on purpose

Page content (a blank page returns 200; the deploy smoke tests own that), `testmap`, `map`,
`dash`, `data`, `admin` and the `test-*` names (same stacks as the four probed), latency and
certificate alerts on the checks (Cloudflare's edge certificate is Cloudflare's to renew, and an
expired origin certificate trips the down check as a 526), and any heartbeat service. The
Mender auto-accept timer on the Mender droplet has no HTTP surface and is not watched.
`adsb-prod` has the resource alerts by tag but no uptime check; adding one is a follow-up once
its health endpoint is known.
