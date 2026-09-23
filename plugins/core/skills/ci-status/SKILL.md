---
name: ci-status
description: Use whenever you need to know whether a pull request's CI passed, to wait for CI after a push, or to judge the run a merge to main started. Replaces `gh pr checks`, `gh pr checks --watch` and `gh run watch`, whose exit codes and tables report skipped, superseded and not-yet-started runs as passes.
---

# ci-status

Reports a PR's real CI state from the runs for its head commit, and exits
non-zero unless every gate passed. The script's docstring lists the traps it
handles; the short version is that `gh pr checks` and `gh run watch` have each
reported green for a PR that was untested, conflicting, failed or unreviewed.

`CI_STATUS="${CLAUDE_PLUGIN_ROOT}/skills/ci-status/scripts/ci_status.py"`

## Use

```
python3 "$CI_STATUS" <pr> -R <owner>/<repo>        # one reading
python3 "$CI_STATUS" <pr> -R <owner>/<repo> --watch  # poll until it settles
python3 "$CI_STATUS" --commit <sha> -R <owner>/<repo> # a merge's push run
```

- Inside a clone of the repo, `-R` and the PR number can be left out; the PR
  defaults to the current branch's. A fork's clone resolves to whichever repo
  `gh` is set to there (often the upstream), so pass `-R` in one.
- `--watch` polls every 30 s for up to 60 min. Run it in the background (it
  outlives a foreground command's limit) and act on its exit status.
- `-v` lists every job rather than only those not passing.
- `--no-review` drops the Claude review from the gate. Use it only when a human
  has reviewed the PR instead.

## Reading the answer

| Exit | Meaning | What to do |
|------|---------|------------|
| 0 | Every gate passed on the PR's head | Read the review it links, if any: green is not "no findings" |
| 1 | Failed, or will not run until someone acts | Act on the reason it prints (below) |
| 2 | The question was wrong: no such PR, no PR for this branch, not a GitHub repo, or no access | Fix the arguments |
| 3 | Not settled: runs still going, or something not arrived yet (a run, the review, the head following its branch) | Ask again, or `--watch`, which calls a wait final after a few minutes |
| 4 | GitHub could not be read, so there is no verdict | Ask again; it says nothing about CI |

Checks from other apps and commit statuses count as gates beside the Actions
runs.

The reasons that need action:

- **A job failed.** Fix it, or report it as a flake. Do not rerun silently: the
  rerun overwrites the run's conclusion (ci-status still lists the failed
  attempt).
- **The PR conflicts.** GitHub makes no merge ref, so no CI will run. Rebase.
- **Every run skipped all its jobs.** Nothing was tested, usually because the
  PR is a draft or a filter excluded the change.
- **The PR's head has not followed its branch.** No CI runs for the new commit.
  Amend to a new SHA (`git commit --amend --no-edit`) and push with
  `--force-with-lease`.
- **The review bot did not review.** The PR edits the review workflow (review it
  by hand), the branch carries an older copy of that workflow than the default
  branch (rebase onto it), or the workflow did not trigger for this head. Report
  any of them as "not reviewed", never as a clean review.
- **The review stopped partway.** Rerun it with the command it prints,
  `gh run rerun <run id>`. `--failed` reruns nothing when the job itself passed,
  which it does unless the repo's workflow checks the review finished.

Skipped jobs inside a run that ran are neutral: deploy jobs skip on every PR.
