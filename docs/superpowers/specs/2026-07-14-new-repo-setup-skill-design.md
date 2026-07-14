# Design: `core:setup-repo` — one-command new-repo setup

**Date:** 2026-07-14
**Status:** Approved (pending spec review)
**Repo:** offworldlabs/claude-shared

## Problem

Setting up a new Offworld Labs repo to org standards (Claude Code enablement, CI,
stack tooling) is manual, undocumented, and inconsistent — the sibling-repo scan
found ruff configured in only 3 of ~10 Python repos, no shared formatter/test
conventions in TS, and no repo with pre-commit, `.editorconfig`, or version
pinning. `claude-shared` should be the single place that encodes "how we set up a
repo," and the setup should be driven **by Claude Code, not a human checklist**:
open a blank repo, start Claude, say *"set this repo up per `claude-shared`,"* and
it happens.

## Goals

- A `core:setup-repo` skill that scaffolds a new repo to org standard in one shot.
- Covers three categories: **Claude Code enablement**, **CI/CD workflows**,
  **stack scaffolding**. (Repo governance — CODEOWNERS, branch protection — is
  explicitly out of scope.)
- Works offline in any repo where `core` is installed; deterministic; idempotent;
  never silently clobbers existing files.

## Non-goals

- Governance/hygiene files (CODEOWNERS, branch protection, PR/issue templates).
- C++ scaffolding (blah2-arm, retina-spectrum) — deferred to a later phase.
- Human-readable setup checklists as the primary interface (the skill is the
  interface; docs are supporting reference).

## Decisions (locked)

### Delivery model — self-contained plugin
The skill and **all** template assets are bundled inside the plugin and copied
into the target repo via `${CLAUDE_PLUGIN_ROOT}`. No runtime fetch. The plugin
`version` bump remains the org-wide update signal. Rules are **copied** into
repos (not symlinked), because symlinking into the plugin cache is fragile.

### Stack defaults (from the sibling-repo scan)
- **Python** (dominant, ~10 repos): pip + `requirements.txt`; **pytest**; **ruff**
  with `target-version = "py312"`, `line-length = 120`, `select = ["E","F","W"]`,
  `format.quote-style = "double"`.
- **TypeScript**: npm; two variants —
  - `ts-frontend`: TypeScript + Vite + Vitest + ESLint 9 (flat) + typescript-eslint + React 18.
  - `ts-backend`: TypeScript + tsx + Vitest + ESLint 9 (flat) + typescript-eslint.
- Greenfield additions (nothing in the org has them today): `.editorconfig`,
  optional pre-commit.

### Prerequisite
Devs install `core@offworld` at **user scope** once, so the skill is available in
a brand-new repo that has no `.claude/settings.json` yet. The skill then writes
the repo's own `.claude/settings.json`, making the repo self-enabling thereafter.

## Repository restructure

The plugin becomes the single source of truth for scaffolded files. The
`templates/` directory added in PR #1 is **folded into the plugin** (PR #1 is
unmerged, so we restructure rather than duplicate). `docs/` stays at the repo root
as the human/agent knowledge hub. Final layout:

```
plugins/core/
  .claude-plugin/plugin.json            # version bump = update signal
  skills/
    pr-description/SKILL.md              # existing
    setup-repo/
      SKILL.md                          # the ordered procedure
      assets/
        claude/
          settings.json                 # extraKnownMarketplaces + enabledPlugins
          CLAUDE.md                     # starter template (<200-line ceiling note)
        rules/
          security.md
          code-style.md
        ci/
          claude-code-review.yml        # write-permission fix baked in
          claude.yml
          ci-python.yml                 # ruff check + ruff format --check + pytest
          ci-node.yml                   # eslint + tsc + vitest
        stack/
          python/
            pyproject.toml              # ruff py312/120/EFW + format; pytest config
            requirements.txt
            requirements-dev.txt        # ruff, pytest
            gitignore                   # Python (shipped without leading dot; skill renames)
            tests/.gitkeep
          ts-frontend/
            package.json                # vite, react, vitest, eslint9, typescript-eslint
            tsconfig.json
            eslint.config.js
            vitest.config.ts
            gitignore                   # Node
          ts-backend/
            package.json                # tsx, tsc, vitest, eslint9, typescript-eslint
            tsconfig.json
            eslint.config.js
            vitest.config.ts
            gitignore                   # Node
        editorconfig                    # shared across all repos
docs/                                   # stays at root (architecture, contracts, decisions, runbooks)
rules/                                  # REMOVED at root — canonical copy now lives in plugin assets
templates/                             # REMOVED at root — folded into plugin assets
```

Note: asset files that must ship as dotfiles (`.gitignore`, `.editorconfig`) are
stored **without** the leading dot in the plugin (so they aren't hidden/ignored in
the marketplace repo) and the skill renames them on copy. `claude-shared`'s own
`.github/workflows/` (the live Claude review workflows) are unchanged and separate
from the `ci/` asset templates.

## The `setup-repo` procedure

Ordered, idempotent, **never silently clobbers**:

1. **Confirm target.** Is this a git repo? If not, offer `git init`. Note whether
   it's empty.
2. **Determine stack.** Detect from existing files (`pyproject.toml`/`requirements*`
   → python; `package.json`/`tsconfig.json` → ts) or ask:
   `python` / `ts-frontend` / `ts-backend` / `none`.
3. **Claude enablement (always).** Write `.claude/settings.json`; create `CLAUDE.md`
   from template **only if absent**; copy rules → `.claude/rules/`.
4. **CI.** Copy the Claude workflows + the stack's CI into `.github/workflows/`.
   Remind about the default-branch guard and the `CLAUDE_CODE_OAUTH_TOKEN` secret
   (cross-reference `docs/runbooks/github-actions-claude-review.md`).
5. **Stack scaffolding.** Copy the chosen stack assets, merging/skipping existing
   files (e.g. don't overwrite an existing `package.json` — report and let the dev
   reconcile).
6. **Shared.** Copy `.editorconfig` and the stack `.gitignore`.
7. **Report.** List every file written/skipped, then a manual follow-up checklist:
   add the `CLAUDE_CODE_OAUTH_TOKEN` secret, install deps, commit workflows to the
   default branch, optional branch protection.

### Idempotency & updates
Re-running on an existing repo brings config up to the current standard: for any
file that already exists and differs, show the diff and ask before overwriting.
A clean re-run (no changes) reports "already up to standard."

### Error handling
- Not a git repo → offer `git init`, else abort with guidance.
- Existing files → merge or skip with an explicit report; never blind-overwrite.
- No `gh` auth / can't set secret → surface as a manual step, don't fail the run.

## Testing

- **Asset validity:** each bundled asset is well-formed — `pyproject.toml` parses,
  `package.json` is valid JSON, workflow/CI YAML is valid, `claude plugin validate`
  passes for the plugin.
- **Procedure:** a script scaffolds into a throwaway temp git repo and asserts the
  expected files land, then runs `ruff check` / `ruff format --check` / `pytest`
  (python) and `eslint` / `tsc --noEmit` / `vitest run` (ts) against the generated
  config to prove the defaults are internally consistent and pass on an empty repo.

## Phasing

Each phase is its own plan → implementation cycle.

- **Phase 1** — `setup-repo` skill + Claude enablement + Claude workflows +
  **Python stack** + fold PR #1 `templates/` into the plugin. Covers ~10/14 repos
  and delivers the end-to-end vision for the dominant stack.
- **Phase 2** — `ts-frontend` + `ts-backend` stacks + `ci-node.yml`.
- **Phase 3 (optional, later)** — pre-commit, C++ (blah2-arm, retina-spectrum).

## Open follow-ups (not blocking)

- Whether the skill should also offer to run the first install (`pip install`,
  `npm ci`) or leave it to the dev — lean toward reporting the command, not running it.
- Whether `CLAUDE.md` should be generated with repo-specific detail the skill
  infers vs. left as the template stub — start with the stub, iterate later.
