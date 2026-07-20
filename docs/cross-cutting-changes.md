# Cross-cutting changes — "I need to change X, where do I look?"

A blast-radius guide for edits that span repos. Each entry names the contract or
mechanism, the repos that touch it, and what else moves when you change it. Pair
this with the connection matrix in [`architecture.md`](./architecture.md) §6.

- **The detection-frame format** (`delay` µs / `doppler` Hz / `snr` dB / optional
  `adsb`, JSONL with parallel arrays): produced by **blah2-arm** and **adsb2dd**;
  consumed by **retina-tracker** and **retina-analytics** (imported in-process inside
  the central server); mimicked by **retina-simulation**. Change one → update all.
  This is the highest-blast-radius contract in the system.

- **Tower ranking logic:** **duplicated** in
  `Tower-Finder/backend/.../tower_ranking.py` and
  `tower-finder-service/backend/tower_ranking.py` — edit both until deduplicated.
  **retina-spectrum** and **retina-gui** are downstream HTTP consumers of `/api/towers`.

- **SDRplay hardware / library version (3.15.2):** shared by **blah2-arm**,
  **retina-spectrum**, and baked into **owl-os**. `blah2` and `retina-spectrum` are
  **mutually exclusive** on the single RSPduo — check the compose profile and the
  `sdrplay_apiService` kill logic in both before changing capture/retune behavior.

- **The on-node service set / ports:** owned by **retina-node**'s docker-compose +
  `config-merger`. Version vars (`BLAH2_V`, `TAR1090_V`, …) and service names are also
  referenced by **node-infra** and **retina-gui** — keep them in sync.

- **Node config schema** (`config.yml`, RX/TX/frequency): authored via **retina-gui**
  → merged by **retina-node** `config-merger` (default → user → forced) → read by
  **blah2-arm** and **retina-geolocator**.

- **Tracker / geolocator / analytics algorithms:** the libraries **retina-tracker** /
  **retina-geolocator** / **retina-analytics** are vendored as git submodules in
  **Tower-Finder** and run in-process. A change means bumping the submodule in
  Tower-Finder and redeploying the central server (not a separate tracker service).

- **OTA / fleet onboarding flow:** spans **owl-os** (Mender inventory scripts) →
  **node-infra** (auto-accept + deploy) → **retina-gui** (`wizard_pending` gate) →
  **retina-node** (Mender artifact). All four participate.

- **The `retina-edge` Docker network / `*.retina.fm` deployment:** shared by
  **tower-finder-service** and the Tower-Finder-hosted nginx vhost on the central
  droplet. See [`architecture.md`](./architecture.md) §4 for the live-endpoint table.
