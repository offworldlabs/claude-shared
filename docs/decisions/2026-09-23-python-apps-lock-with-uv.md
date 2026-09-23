# Python apps lock their dependencies with uv

- **Date:** 2026-09-23. **Status:** proposed; accepted when this merges.
- **Scope:** Python apps. Whether the five vendored `retina-*` libraries commit a lock is a
  separate question, open in ClickUp `86cb49y4k`, and this record does not settle it.
- **Ticket:** ClickUp `123zgec4jmx`. **Follow-up:** `123zgec4jn0`, the other apps.

## 1. Context

The `setup-repo` standard installs every Python repo the same way:
`uv pip install -r requirements.txt -r requirements-dev.txt`. The requirements files pin the
direct dependencies and nothing else, so every install resolves the rest of the tree afresh.

For a deployed app that means the image, CI and each developer's venv can each run a different
tree. retina-server pinned 15 of the 54 third-party packages its image runs; pydantic,
SQLAlchemy, websockets and the rest were chosen again whenever the image's dependency layer
rebuilt. On
2026-09-23 a developer venv differed from production on pydantic (2.13.4 against 2.13.5) and
websockets (16.1.1 against 17.1), with nothing in either repository to say which was intended.

## 2. Decision

An **app** is a repo that runs as a deployed service or a tool, and that no other repo installs
as a dependency. Apps are uv projects:

- `pyproject.toml` declares the runtime dependencies under `[project]` and the tooling under
  `[dependency-groups] dev`. `[tool.uv] package = false` unless the app is itself installed.
- `uv.lock` is committed and is the only record of what gets installed. There is no
  `requirements.txt`.
- CI runs `uv sync --locked`, which fails when the lock no longer matches `pyproject.toml`.
- Where the image pins uv as `ARG UV_VERSION`, CI installs that version, read from the
  Dockerfile, and fails unless it reads exactly one `x.y.z`: setup-uv takes an empty version as
  its latest. Locks are written with the same uv (`uv tool run uv@<version> lock`).
- Images run `uv sync --locked --no-dev` into a virtualenv put first on `PATH`, not into the
  system site-packages: `uv sync` removes whatever the lock does not name, the base image's own
  `pip` included.
- Libraries vendored as submodules are `[tool.uv.sources]` path entries, editable for local work
  and installed with `--no-editable` in images.

## 3. Consequences

- A dependency change and its lock land in the same commit. So does a submodule bump that changes
  a vendored library's own dependencies, which is the easy one to miss; `--locked` in CI catches
  it.
- Upgrades are deliberate: `uv lock --upgrade-package <name>`, or `uv lock --upgrade` for the
  whole tree. Nothing relocks on its own, so a transitive security release reaches an app only
  when someone relocks. No Python repo runs a dependency bot today. Dependabot's `uv` ecosystem
  could do that job, and adopting it is a separate decision.
- Moving an app to a lock need not move any version. Seed the first `uv lock` with
  `[tool.uv] constraint-dependencies` listing what production runs, then delete the constraints
  and lock again: uv keeps a locked version until told to upgrade it, so the lock ends at the
  deployed versions and the first image built from it matches the running one.
- The uv that writes a lock and the uv that reads it need not match. A lock written by 0.12.5
  syncs under 0.9.22. Pinning CI to the image's uv therefore buys reproducibility more than
  compatibility: a uv release cannot change CI without a commit, and one edit to `UV_VERSION`
  moves CI, image and relock together. Where CI does not build the image, it is also the only
  check before merge that the image's uv accepts the lock.

## 4. Adoption

`setup-repo` gains a `python-app` stack that scaffolds §2. Its `python` stack stays as it is and
remains the scaffold for libraries. retina-server moves first. tower-finder-service,
retina-telemetry, retina-gui and node-infra's `mender-auto-accept` install with plain pip today
and move under `123zgec4jn0`. The scaffold has no Dockerfile, so the CI pin is added with the
image: tower-finder-service#42's `id: uv` step is the pattern for one job, and retina-server#572
wraps it in a composite action for several.
