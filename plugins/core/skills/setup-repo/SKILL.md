---
name: setup-repo
description: Use when setting up a new or blank Offworld Labs repository, or when the user asks to "set up this repo per claude-shared", scaffold a repo to org standards, or add the standard Claude/CI/tooling setup. Scaffolds Claude Code enablement, the Claude review workflows, and stack-specific tooling for the repo.
---

# Set up a repo per claude-shared

Scaffold the current repository to Offworld Labs standards: Claude Code
enablement, the Claude review workflows, and the chosen stack's tooling. The
mechanical file copying is done by the bundled engine; you handle the
interactive parts and the report.

`ENGINE="${CLAUDE_PLUGIN_ROOT}/skills/setup-repo/scripts/scaffold-repo.sh"`

## Procedure

1. **Confirm the target.** Ensure the working directory is a git repo
   (`git rev-parse --is-inside-work-tree`). If it is not, offer to run
   `git init`; abort if the user declines.

2. **Determine the stack.** Detect from existing files: `pyproject.toml` or
   `requirements*.txt` → `python`. If ambiguous or empty, ask the user to choose
   `python` or `none` (ts-frontend / ts-backend arrive in a later phase).

3. **Scaffold the files.** Run the engine, which never overwrites existing files:
   `bash "$ENGINE" . <stack>`
   Relay its `WRITTEN` / `SKIPPED` output to the user.

4. **Install dependencies.** For `python`, run
   `pip install -r requirements.txt -r requirements-dev.txt`
   (prefer an active virtualenv). Report the command and result; if the
   toolchain is unavailable, skip and note it rather than failing.

5. **Flesh out CLAUDE.md.** The stub was just written. Ask the user for a
   one-or-two-line description of what this repo does, then fill in the
   `Project Overview`, `Build & Test Commands`, and `Local Architecture`
   sections from their answer plus what was scaffolded (stack, `ruff check .`,
   `ruff format --check .`, `pytest`). If they skip, leave the stub as-is. Keep
   CLAUDE.md under the 200-line ceiling noted in the template.

6. **Report and follow-ups.** Summarise files written vs skipped, then list the
   manual steps: add the `CLAUDE_CODE_OAUTH_TOKEN` repo secret, and commit the
   workflows to the default branch before Claude review runs (see
   `docs/runbooks/github-actions-claude-review.md` for why). Do not commit on the
   user's behalf unless asked.
