# Runbook: Claude Code review workflow runs green but posts no comment

## Symptom

You set up the Claude GitHub Actions in a new repo (via `/install-github-app`).
The "Claude Code Review" job shows a green check on every PR, but **no review
comment ever appears**.

## Cause

The scaffold that `/install-github-app` generates grants the workflow a
**read-only** token:

```yaml
permissions:
  contents: read
  pull-requests: read   # can read the diff, cannot post
  issues: read
  id-token: write
```

The review runs and analyses the diff, then is **denied** when it tries to post
the comment. The job still exits green because a failed post is not a job
failure. Confirm in the run log:

```bash
gh run view <run-id> --log | grep -iE 'permission_denials_count|PullRequests:'
# "permission_denials_count": 1   ← the denied action was posting the comment
# PullRequests: read              ← the read-only grant
```

> Note: "green check, no comment" is genuinely ambiguous between this and "clean
> code, nothing to flag." Always read the run log rather than assuming.

## Fix

Grant write access in **both** workflow files:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
  id-token: write
```

The fastest path in a new repo is to skip the broken scaffold entirely and run
the `core:setup-repo` skill, which installs the corrected workflows. Ask
Claude:

> set this repo up per `claude-shared`

If you need to copy the workflows manually, they live in the `core` plugin's
assets and copy as-is into `.github/workflows/` (no leading-dot rename needed):

```bash
mkdir -p .github/workflows
cp path/to/claude-shared/plugins/core/skills/setup-repo/assets/ci/claude-code-review.yml .github/workflows/
cp path/to/claude-shared/plugins/core/skills/setup-repo/assets/ci/claude.yml            .github/workflows/
```

## Critical gotcha: the fix must land on the default branch first

`claude-code-action` refuses to run when the workflow file on a PR branch
differs from the copy on the default branch — a security guard so a PR can't
rewrite the review workflow to exfiltrate secrets. Log message:

```
Workflow validation failed. The workflow file must exist and have identical
content to the version on the repository's default branch.
```

Consequences:

- You **cannot** validate a workflow change on the PR that makes the change.
  Editing the workflow on a feature branch makes the review go *silent* on that
  PR.
- Merge the workflow change to `main` (default branch) first. It takes effect on
  the **next** normal PR opened afterward.
- A PR opened *before* the change, whose workflow now differs from the updated
  default, is also skipped until rebased onto the new default.

## Verify

After the fix is on `main`, open a normal PR (one that does **not** touch
`.github/workflows/`) and confirm a `claude[bot]` comment appears.

## Security note

`pull-requests: write` on a `pull_request` trigger is sensitive only if the repo
accepts **fork** PRs — untrusted fork code could request the write token. For
private, internal-only org repos with no forks the risk is negligible. If you
expect external forks, use `pull_request_target` with author restrictions
instead.
