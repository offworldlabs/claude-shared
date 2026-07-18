---
name: adopting-core-setup-repo
description: |
  Reconciliation playbook for piloting/adopting Offworld Labs' `core:setup-repo`
  skill in an EXISTING repo (not a blank one). Use when: (1) running "set this repo
  up per claude-shared" against a repo that already has some standard files,
  (2) the scaffolded `ci-python.yml` fails with `ModuleNotFoundError: No module
  named '<pkg>'` in CI, (3) a Claude review workflow runs green but posts no
  comment even after granting write perms, (4) scaffolded `.claude/settings.json`
  or `.claude/rules/` never show up in `git status`, (5) `permission_denials_count`
  is non-zero but you're unsure if posting actually failed, (6) hardening the
  `@claude` workflow on a PUBLIC repo. Covers the files the engine SKIPS (and must
  be reconciled by hand) and the non-obvious CI/security gotchas.
author: Claude Code
version: 1.0.0
date: 2026-07-18
---

# Adopting core:setup-repo in an existing repo

## Problem

`core:setup-repo` scaffolds Offworld Labs standards, but its engine
(`scaffold-repo.sh`) **never overwrites an existing file** — it `SKIPPED`s them.
In a repo that is already partially standardized, the real work is therefore
*reconciling the skipped files by hand*, plus several non-obvious CI and security
gotchas the bare templates don't handle for a real (packaged, public) repo.

## Context / Trigger Conditions

- Running the skill against an existing repo (has `CLAUDE.md`, workflows,
  `pyproject.toml`, etc. already).
- CI added by the skill fails; or a review workflow is green with no comment.
- Scaffolded `.claude/` files don't appear tracked by git.

## Solution — the five reconciliations that bite

### 1. The engine skips existing files → reconcile them, don't trust the copy
After `bash scaffold-repo.sh . python`, read the `SKIPPED` list. Every skipped
file is your manual work. The dangerous ones are the two Claude workflows: if they
predate the fix they ship `pull-requests: read` / `issues: read` (the "green
review, no comment" bug) and the engine will NOT fix them.

### 2. `ci-python.yml` does not install a packaged repo → pytest ImportError
The template CI runs `uv pip install --system -r requirements.txt -r
requirements-dev.txt` — **dependencies only, not the package**. If tests do
`from <pkg> import ...` and the repo is laid out as an installable package
(`pyproject.toml` with setuptools), CI fails:

```
ModuleNotFoundError: No module named '<pkg>'
```

Tests may pass locally only because a dev venv had `pip install -e .`. Fix without
editing the shared template:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]   # <- lets pytest import the package from source in CI
```

(Alternative: `uv pip install --system -e .` in the CI step, but that forks the
template.)

### 3. Write perms ALONE don't post review comments
The bare template `claude-code-review.yml` grants write perms but that is *not
sufficient*. The `code-review` plugin buffers via
`mcp__github_inline_comment__create_inline_comment`, which must be allow-listed,
or nothing posts even with write scope. The working workflow also needs:

```yaml
          track_progress: true
          claude_args: |
            --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*)"
```

### 4. A `.gitignore` that ignores `.claude/` silently drops scaffolded config
If `.gitignore` has a blanket `.claude/`, the scaffolded `settings.json` +
`rules/` are written to disk but never tracked — `git add` skips them. Un-ignore
the shared config while keeping personal settings ignored:

```
.claude/*
!.claude/settings.json
!.claude/rules/
```

Verify: `git check-ignore -v .claude/settings.json` prints the `!`-negation line
(un-ignored); `.claude/settings.local.json` stays matched by `.claude/*`.

### 5. Public repo → gate the `@claude` workflow to trusted principals
`claude.yml` fires on `@claude` in comments/issues from **anyone** on a public
repo, and once write-scoped that's a HIGH privilege-escalation surface. Add an
`author_association` guard to each clause of the `if:` gate:

```yaml
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude') &&
        (github.event.comment.author_association == 'OWNER' || github.event.comment.author_association == 'MEMBER' || github.event.comment.author_association == 'COLLABORATOR')) ||
      ... (repeat per event; use github.event.review.author_association for pull_request_review,
           github.event.issue.author_association for issues)
```

## Verification

- `ruff check .` / `ruff format --check .` / `pytest` all green — run over `.`
  (whole repo), not just the package dir; the CI gate checks everything and
  catches pre-existing format drift in sibling dirs (e.g. `plotter/`).
- Workflow changes must land on the **default branch first** — `claude-code-action`
  refuses to run when a PR's workflow differs from `main`'s. Verify the review
  comment on a **separate** PR that touches no `.github/workflows/` file.
- **`permission_denials_count > 0` is NOT proof of failure.** With a tight
  `--allowedTools`, Claude attempts non-allowlisted tools during review and those
  are denied *benignly*. The decisive evidence a review posted correctly is:
  the job log shows `PullRequests: write` in the GITHUB_TOKEN permissions block
  AND a `claude[bot]` comment with real content exists. Don't trust the counter.

## Example

Pilot on `offworldlabs/retina-tracker` (claude-shared#5): engine wrote 6 missing
files, skipped 7 existing. Reconciled `.gitignore` (#4), added `pythonpath` (#2),
grafted `track_progress`/`allowedTools` (#3), fixed `claude.yml` perms + guard
(#5). CI green; a real `claude[bot]` comment verified on a separate docs-only PR
despite `permission_denials_count: 3` (benign allowlist gating).

## Notes

- Keep `requires-python` where it is; only move ruff `target-version` to match the
  CI Python. They can differ (target-version affects lint assumptions; a repo can
  still support older runtimes for ARM/edge).
- Don't fork the org-standard files per-repo for hardening/pinning — apply the
  local guard where a HIGH finding demands it, and file template improvements as
  follow-ups on `offworldlabs/claude-shared`.

## References

- `claude-shared` runbook: `docs/runbooks/github-actions-claude-review.md`
- Related skill: `claude-code-action-review-not-posting-comments` (covers the
  read-vs-write perms cause; this skill adds the allowedTools requirement and the
  benign-denial-counter refinement).
