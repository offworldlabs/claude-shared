"""ci_status.py's verdicts against a fake GitHub.

Each case is a way CI has been misread with `gh pr checks` or `gh run watch`.
The verdict has to come out right in both directions: the traps must not read as
green, and the harmless look-alikes (a cancelled duplicate, an edit's skipped
run, a failure that a rerun fixed) must not read as red.
"""

from __future__ import annotations

import base64
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "plugins/core/skills/ci-status/scripts/ci_status.py"
_spec = importlib.util.spec_from_file_location("ci_status", _SCRIPT)
cs = importlib.util.module_from_spec(_spec)
sys.modules["ci_status"] = cs
_spec.loader.exec_module(cs)

REPO = "org/app"
HEAD = "a" * 40
OLD = "b" * 40
REVIEW_PATH = ".github/workflows/claude-code-review.yml"
TRACKED = "steps:\n  - uses: anthropics/claude-code-action@v1\n    with:\n      track_progress: true\n"
UNTRACKED = "steps:\n  - uses: anthropics/claude-code-action@v1\n"


T1, T2 = "2026-09-23T10:00:00Z", "2026-09-23T10:01:00Z"
T0 = "2026-09-23T09:00:00Z"
MAIN = "9" * 40  # the default branch's head
# The review workflow's recent history on the default branch.
HISTORY = f"repos/{REPO}/commits?sha={MAIN}&path={REVIEW_PATH}&per_page=10"


def _change(sha, dated, merged_at=None):
    """A commit to the review workflow, dated `dated`, landed by a PR merged at `merged_at` if any."""
    pulls = [{"merged_at": merged_at, "base": {"ref": "main"}}] if merged_at else []
    return {"sha": sha, "commit": {"committer": {"date": dated}}}, {f"repos/{REPO}/commits/{sha}/pulls": pulls}


def _run(run_id, name="CI", *, event="pull_request", status="completed", conclusion="success", attempt=1, at=T1):
    path = REVIEW_PATH if name == "Claude Code Review" else ".github/workflows/ci.yml"
    return {
        "id": run_id,
        "name": name,
        "path": path,
        "event": event,
        "status": status,
        "conclusion": conclusion,
        "run_attempt": attempt,
        "created_at": at,
        "run_started_at": at,
    }


def _jobs(*pairs):
    return [{"name": n, "status": "completed" if c else "in_progress", "conclusion": c} for n, c in pairs]


def _started(jobs):
    """The same jobs, each taken by a runner that got as far as its first step."""
    return [{**j, "steps": [{"name": "Set up job"}]} for j in jobs]


def _content(text, sha):
    return {"sha": sha, "content": base64.b64encode(text.encode()).decode()}


def _comment(run_id, *, ticked=True, at=T2):
    box = "x" if ticked else " "
    body = (
        f"**Claude finished** [View job](https://github.com/{REPO}/actions/runs/{run_id})\n\n"
        f"- [x] Gather context\n- [{box}] Post findings\n"
    )
    return {
        "id": 11,
        "created_at": at,
        "user": {"login": "claude[bot]", "type": "Bot"},
        "body": body,
        "html_url": "https://example.test/c1",
    }


class FakeGitHub:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []
        self.fixed_versions = {}

    def _answer(self, path):
        self.calls.append(path)
        if path not in self.routes:
            raise cs.GhError(["api", path], "gh: Not Found (HTTP 404)")
        return self.routes[path]

    def get(self, path, *, fixed=False):
        return self._answer(path)

    def items(self, path, key=None, *, fixed=False, version=""):
        if fixed is True:
            self.fixed_versions[path] = version
        return self._answer(path)


def _pr(**over):
    pr = {
        "number": 7,
        "state": "open",
        "merged": False,
        "draft": False,
        "mergeable": True,
        "mergeable_state": "clean",
        "head": {"sha": HEAD, "ref": "feat/x", "repo": {"full_name": REPO}},
        "base": {"ref": "main", "sha": "c" * 40, "repo": {"default_branch": "main"}},
    }
    pr.update(over)
    return pr


def _routes(**over):
    """A PR whose CI passed and whose review finished and commented."""
    routes = {
        f"repos/{REPO}/pulls/7": _pr(),
        f"repos/{REPO}/git/ref/heads/feat/x": {"object": {"sha": HEAD}},
        f"repos/{REPO}/git/ref/heads/main": {"object": {"sha": MAIN}},
        f"repos/{REPO}/actions/runs?head_sha={HEAD}&per_page=100": [_run(1), _run(2, "Claude Code Review")],
        f"repos/{REPO}/commits/{HEAD}/check-runs?per_page=100": [],
        f"repos/{REPO}/commits/{HEAD}/status?per_page=100": [],
        f"repos/{REPO}/actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "success"), ("deploy", "skipped")),
        f"repos/{REPO}/actions/runs/2/attempts/1/jobs?per_page=100": _jobs(("claude-review", "success")),
        f"repos/{REPO}/pulls/7/files?per_page=100": [{"filename": "src/app.py"}],
        f"repos/{REPO}/contents/{REVIEW_PATH}?ref={MAIN}": _content(TRACKED, "w1"),
        f"repos/{REPO}/contents/{REVIEW_PATH}?ref={HEAD}": _content(TRACKED, "w1"),
        f"repos/{REPO}/issues/7/comments?per_page=100": [_comment(2)],
        f"repos/{REPO}/pulls/7/comments?per_page=100": [],
        HISTORY: [],
    }
    routes.update({(k if k.startswith("repos/") else f"repos/{REPO}/{k}"): v for k, v in over.items()})
    return routes


def _assess(routes, *, local=None, standing="behind", review=True):
    gh = FakeGitHub(routes)
    out = cs.assess_pr(
        gh, REPO, 7, review=review, local=lambda repo, ref, head: (local, standing), sleep=lambda s: None
    )
    return out, gh


def _text(out):
    return "\n".join(out.lines) + "\n" + out.verdict()


def test_a_passing_pr_with_a_finished_review_is_green():
    out, _ = _assess(_routes(), local=HEAD)
    assert out.state == cs.GREEN, _text(out)
    assert "https://example.test/c1" in _text(out)
    assert f"gh api repos/{REPO}/issues/comments/11 --jq .body" in _text(out)


def test_an_edited_run_whose_jobs_all_skipped_does_not_hide_the_real_one():
    runs = [_run(3, at=T2), _run(1, at=T1, conclusion="failure"), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/3/attempts/1/jobs?per_page=100": _jobs(("tests", "skipped"), ("deploy", "skipped")),
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "failure")),
            }
        )
    )
    assert out.state == cs.FAILED
    assert "tests failure" in out.verdict()
    assert "every job skipped" in _text(out)


def test_a_cancelled_duplicate_from_a_stack_push_is_set_aside():
    runs = [_run(5, conclusion="cancelled", at=T2), _run(1, at=T1), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/5/attempts/1/jobs?per_page=100": _jobs(("tests", "cancelled")),
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert "superseded by run 1" in _text(out)


def test_a_job_a_cancelled_run_cut_short_is_not_hidden_by_an_edit_s_run():
    # A timeout cancels the job and the run; an edit's run then skips the tests.
    runs = [_run(3, at=T2), _run(1, conclusion="cancelled", at=T1), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/3/attempts/1/jobs?per_page=100": _jobs(("tests", "skipped"), ("contract", "success")),
                "actions/runs/1/attempts/1/jobs?per_page=100": _started(
                    _jobs(("tests", "cancelled"), ("contract", "success"))
                ),
            }
        )
    )
    assert out.state == cs.FAILED, _text(out)
    assert "tests cancelled" in out.verdict()
    assert "(from run 1)" in _text(out)


@pytest.mark.parametrize("cancelled_at", [T1, "2026-09-23T10:02:00Z"], ids=["older", "newer"])
def test_a_cancelled_duplicate_lends_no_job_it_never_queued(cancelled_at):
    # The survivor skips the deploy chain; the duplicate concurrency cancelled lists it, never queued, as cancelled.
    runs = [_run(1, at=T2), _run(5, conclusion="cancelled", at=cancelled_at), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/5/attempts/1/jobs?per_page=100": [
                    {**j, "steps": [], "runner_id": None}
                    for j in _jobs(("tests", "cancelled"), ("deploy", "cancelled"))
                ],
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert "(from run 5)" not in _text(out)


def test_a_job_is_queued_once_it_has_a_runner_id_or_a_step():
    answer = [
        {"name": "a", "status": "completed", "conclusion": "cancelled", "steps": [], "runner_id": 0},
        {"name": "b", "status": "completed", "conclusion": "cancelled", "steps": [{"name": "x"}], "runner_id": None},
        {"name": "c", "status": "completed", "conclusion": "cancelled", "steps": [], "runner_id": 7},
        {"name": "d", "status": "completed", "conclusion": "cancelled", "steps": [], "runner_id": None},
        {"name": "e", "status": "completed", "conclusion": "cancelled"},
    ]
    gh = FakeGitHub({f"repos/{REPO}/actions/runs/9/attempts/1/jobs?per_page=100": answer})
    jobs = cs.attempt_jobs(gh, REPO, 9, 1, finished=True)
    assert [j.queued for j in jobs] == [True, True, True, False, False]


def test_a_run_cancelled_by_hand_while_its_tests_queued_is_not_hidden_by_an_edit_s_run():
    runs = [_run(3, at=T2), _run(1, conclusion="cancelled", at=T1), _run(2, "Claude Code Review")]
    queued = [{**j, "steps": [], "runner_id": 0} for j in _jobs(("tests", "cancelled"), ("contract", "cancelled"))]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/3/attempts/1/jobs?per_page=100": _jobs(("tests", "skipped"), ("contract", "success")),
                "actions/runs/1/attempts/1/jobs?per_page=100": queued,
            }
        )
    )
    assert out.state == cs.FAILED, _text(out)
    assert "tests cancelled" in out.verdict()


def test_a_live_run_lends_ahead_of_a_cancelled_one():
    runs = [
        _run(3, at=T2),
        _run(4, conclusion="cancelled", at="2026-09-23T10:00:30Z"),
        _run(1, at=T1),
        _run(2, "Claude Code Review"),
    ]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/3/attempts/1/jobs?per_page=100": _jobs(("tests", "skipped"), ("contract", "success")),
                "actions/runs/4/attempts/1/jobs?per_page=100": _started(_jobs(("tests", "cancelled"))),
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "success")),
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert "success     tests  (from run 1)" in _text(out)


def test_a_run_that_reads_completed_while_a_job_runs_is_pending():
    out, _ = _assess(_routes(**{"actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", None))}))
    assert out.state == cs.PENDING
    assert "CI still running (0/1 jobs done)" in out.verdict()


def test_a_run_that_concluded_failure_with_no_failing_job_still_fails():
    runs = [_run(1, conclusion="startup_failure"), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/1/attempts/1/jobs?per_page=100": [],
            }
        )
    )
    assert out.state == cs.FAILED
    assert "startup_failure" in out.verdict()


def test_no_runs_yet_is_pending_not_green():
    out, _ = _assess(_routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": []}))
    assert out.state == cs.PENDING
    assert "no runs yet" in out.verdict()


def test_a_conflicting_pr_fails_because_no_ci_will_run():
    out, _ = _assess(_routes(**{"pulls/7": _pr(mergeable=False, mergeable_state="dirty")}))
    assert out.state == cs.FAILED
    assert "no merge ref" in out.verdict()


def test_unknown_mergeability_is_asked_again_then_pending():
    out, gh = _assess(_routes(**{"pulls/7": _pr(mergeable=None, mergeable_state="unknown")}))
    assert out.state == cs.PENDING
    assert gh.calls.count(f"repos/{REPO}/pulls/7") == 4


def test_a_branch_the_pr_head_has_not_followed_is_reported():
    out, _ = _assess(_routes(**{"git/ref/heads/feat/x": {"object": {"sha": OLD}}}))
    assert f"stuck-head@{HEAD}" in out.waits
    assert out.state == cs.PENDING
    assert "force-with-lease" in out.verdict()


def test_a_local_branch_elsewhere_is_named_but_does_not_change_the_verdict():
    out, _ = _assess(_routes(), local=OLD)
    assert out.state == cs.GREEN
    assert f"local feat/x is at {OLD[:10]}" in _text(out)


def test_a_failure_a_rerun_fixed_is_green_and_still_shown():
    runs = [_run(1, attempt=2), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/1/attempts/2/jobs?per_page=100": _jobs(("tests", "success")),
                "actions/runs/1/attempts/1": {"conclusion": "failure"},
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "failure"), ("lint", "success")),
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert "attempt 1 was failure: tests" in _text(out)


def test_a_pr_that_edits_the_review_workflow_is_not_reviewed():
    out, _ = _assess(_routes(**{"pulls/7/files?per_page=100": [{"filename": REVIEW_PATH}]}))
    assert out.state == cs.FAILED
    assert "review it by hand" in out.verdict()


def test_a_branch_with_an_older_review_workflow_is_told_to_rebase():
    runs = [_run(1), _run(2, "Claude Code Review", conclusion="failure")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/2/attempts/1/jobs?per_page=100": _jobs(("claude-review", "failure")),
                f"contents/{REVIEW_PATH}?ref={HEAD}": _content(TRACKED, "w0"),
                "issues/7/comments?per_page=100": [],
            }
        )
    )
    assert out.state == cs.FAILED
    assert "rebase" in out.verdict()


def test_a_stale_review_workflow_fails_before_the_review_even_starts():
    runs = [_run(1), _run(2, "Claude Code Review", status="in_progress", conclusion=None)]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/2/attempts/1/jobs?per_page=100": _jobs(("claude-review", None)),
                f"contents/{REVIEW_PATH}?ref={HEAD}": _content(TRACKED, "w0"),
            }
        )
    )
    assert out.state == cs.FAILED
    assert "rebase" in out.verdict()


def test_a_review_that_stopped_partway_fails():
    out, _ = _assess(_routes(**{"issues/7/comments?per_page=100": [_comment(2, ticked=False)]}))
    assert out.state == cs.FAILED
    assert "Post findings" in _text(out)


def test_a_comment_from_an_earlier_review_run_does_not_count():
    out, _ = _assess(_routes(**{"issues/7/comments?per_page=100": [_comment(99)]}))
    assert out.state == cs.FAILED
    assert "did not review" in out.verdict()


def test_a_run_link_quoted_in_a_code_block_does_not_count():
    quoted = _comment(99)
    quoted["body"] += "\n```\nsee /actions/runs/2\n```\n"
    out, _ = _assess(_routes(**{"issues/7/comments?per_page=100": [quoted]}))
    assert out.state == cs.FAILED


def test_an_untracked_review_that_posted_nothing_is_noted_not_failed():
    out, _ = _assess(
        _routes(
            **{
                f"contents/{REVIEW_PATH}?ref={MAIN}": _content(UNTRACKED, "w1"),
                f"contents/{REVIEW_PATH}?ref={HEAD}": _content(UNTRACKED, "w1"),
                "issues/7/comments?per_page=100": [],
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert "does not track progress" in _text(out)


def test_a_repo_without_a_review_workflow_expects_no_review():
    routes = _routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": [_run(1)]})
    del routes[f"repos/{REPO}/contents/{REVIEW_PATH}?ref={MAIN}"]
    out, _ = _assess(routes)
    assert out.state == cs.GREEN, _text(out)


def test_a_review_not_yet_registered_is_pending():
    out, _ = _assess(_routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": [_run(1)]}))
    assert out.state == cs.PENDING
    assert "no Claude review run" in out.verdict()


def test_no_review_skips_the_review_gate():
    out, gh = _assess(_routes(**{"issues/7/comments?per_page=100": []}), review=False)
    assert out.state == cs.GREEN
    assert not any("comments" in call for call in gh.calls)


def test_non_gate_runs_are_counted_not_judged():
    runs = [_run(1, event="push"), _run(9, "Claude Code", event="issue_comment", conclusion="skipped")]
    gh = FakeGitHub(
        {
            f"repos/{REPO}/commits/main": {"sha": HEAD},
            f"repos/{REPO}/commits/{HEAD}/check-runs?per_page=100": [],
            f"repos/{REPO}/commits/{HEAD}/status?per_page=100": [],
            f"repos/{REPO}/actions/runs?head_sha={HEAD}&per_page=100": runs,
            f"repos/{REPO}/actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("deploy", "success")),
        }
    )
    out = cs.assess_commit(gh, REPO, "main")
    assert out.state == cs.GREEN, _text(out)
    assert "1 issue_comment run(s), which are not gates" in _text(out)
    assert f"repos/{REPO}/actions/runs/9/attempts/1/jobs?per_page=100" not in gh.calls


def test_a_skipped_deploy_behind_a_failed_smoke_test_fails_the_commit():
    gh = FakeGitHub(
        {
            f"repos/{REPO}/commits/main": {"sha": HEAD},
            f"repos/{REPO}/commits/{HEAD}/check-runs?per_page=100": [],
            f"repos/{REPO}/commits/{HEAD}/status?per_page=100": [],
            f"repos/{REPO}/actions/runs?head_sha={HEAD}&per_page=100": [_run(1, event="push", conclusion="failure")],
            f"repos/{REPO}/actions/runs/1/attempts/1/jobs?per_page=100": _jobs(
                ("Staging smoke tests", "failure"), ("Deploy to production", "skipped")
            ),
        }
    )
    out = cs.assess_commit(gh, REPO, "main", verbose=True)
    assert out.state == cs.FAILED
    assert "skipped     Deploy to production" in _text(out)


def test_a_comment_from_an_earlier_attempt_of_the_same_run_does_not_count():
    runs = [_run(1), _run(2, "Claude Code Review", attempt=2, at=T2)]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/2/attempts/2/jobs?per_page=100": _jobs(("claude-review", "success")),
                "actions/runs/2/attempts/1": {"conclusion": "success"},
                "issues/7/comments?per_page=100": [_comment(2, at=T1)],
            }
        )
    )
    assert out.state == cs.FAILED
    assert "did not review" in out.verdict()


def test_a_link_to_a_longer_run_id_does_not_count():
    out, _ = _assess(_routes(**{"issues/7/comments?per_page=100": [_comment(21)]}))
    assert out.state == cs.FAILED


def test_inline_comments_are_counted_by_the_commit_they_were_made_on():
    inline = [
        {"user": {"login": "claude[bot]", "type": "Bot"}, "commit_id": HEAD, "original_commit_id": OLD},
        {"user": {"login": "claude[bot]", "type": "Bot"}, "commit_id": HEAD, "original_commit_id": HEAD},
    ]
    out, _ = _assess(_routes(**{"pulls/7/comments?per_page=100": inline}))
    assert "with 1 inline comment(s) made on this head" in _text(out)


def test_an_unreadable_github_exits_4_not_as_a_ci_failure(monkeypatch):
    def refuse(args):
        raise cs.GhError(args, "HTTP 502: Bad Gateway")

    monkeypatch.setattr(cs, "_gh", refuse)
    assert cs.main(["7", "-R", REPO]) == 4


def test_a_newer_run_that_skipped_the_tests_does_not_hide_their_failure():
    runs = [_run(3, at=T2), _run(1, at=T1, conclusion="failure"), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/3/attempts/1/jobs?per_page=100": _jobs(("ci-ok", "success"), ("tests", "skipped")),
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("ci-ok", "failure"), ("tests", "failure")),
            }
        )
    )
    assert out.state == cs.FAILED
    assert "tests failure" in out.verdict()
    assert "ci-ok failure" not in out.verdict()
    assert "tests  (from run 1)" in _text(out)


def test_a_job_list_is_kept_across_polls_only_once_every_job_has_finished(monkeypatch):
    answers = iter(
        [
            '{"name": "tests", "status": "in_progress", "conclusion": null}',
            '{"name": "tests", "status": "completed", "conclusion": "success"}',
        ]
    )
    calls = []

    def gh(args):
        calls.append(args)
        return next(answers)

    monkeypatch.setattr(cs, "_gh", gh)
    github = cs.GitHub()
    assert cs.attempt_jobs(github, REPO, 1, 1, finished=True)[0].state == "in_progress"
    assert cs.attempt_jobs(github, REPO, 1, 1, finished=True)[0].state == "success"
    assert cs.attempt_jobs(github, REPO, 1, 1, finished=True)[0].state == "success"
    assert len(calls) == 2


def test_findings_written_as_a_task_list_are_not_unfinished_steps():
    finished = _comment(2)
    finished["body"] += "\nFindings:\n\n- [ ] Add a test for the empty case\n"
    out, _ = _assess(_routes(**{"issues/7/comments?per_page=100": [finished]}))
    assert out.state == cs.GREEN, _text(out)


def test_a_sticky_comment_edited_during_the_latest_attempt_counts():
    sticky = _comment(2, at="2026-09-23T09:00:00Z")
    sticky["updated_at"] = T2
    out, _ = _assess(_routes(**{"issues/7/comments?per_page=100": [sticky]}))
    assert out.state == cs.GREEN, _text(out)


def test_a_branch_name_is_quoted_into_the_ref_path():
    routes = _routes(**{"pulls/7": _pr(head={"sha": HEAD, "ref": "fix#12", "repo": {"full_name": REPO}})})
    routes[f"repos/{REPO}/git/ref/heads/fix%2312"] = {"object": {"sha": OLD}}
    out, _ = _assess(routes)
    assert f"stuck-head@{HEAD}" in out.waits


@pytest.mark.parametrize("crash", [KeyError("missing"), ValueError("bad timestamp"), TypeError("None")])
def test_a_crash_while_assessing_exits_4_not_as_a_ci_failure(monkeypatch, crash):
    def assess_pr(*args, **kwargs):
        raise crash

    monkeypatch.setattr(cs, "assess_pr", assess_pr)
    assert cs.main(["7", "-R", REPO]) == 4


def test_an_outage_while_finding_the_pr_is_not_a_usage_error(monkeypatch):
    def refuse(args):
        raise cs.GhError(args, "HTTP 503: Service Unavailable")

    monkeypatch.setattr(cs, "_gh", refuse)
    assert cs.main([]) == 4


def test_no_pr_for_the_branch_is_a_usage_error(monkeypatch):
    def refuse(args):
        raise cs.GhError(args, 'no pull requests found for branch "main"')

    monkeypatch.setattr(cs, "_gh", refuse)
    with pytest.raises(SystemExit) as exited:
        cs.main([])
    assert exited.value.code == 2


def test_a_pr_github_does_not_know_is_a_usage_error(monkeypatch):
    def refuse(args):
        raise cs.GhError(args, "gh: Not Found (HTTP 404)")

    monkeypatch.setattr(cs, "_gh", refuse)
    assert cs.main(["9999", "-R", REPO]) == 2


def test_a_quoted_track_progress_still_counts_as_tracked():
    quoted = TRACKED.replace("track_progress: true", 'track_progress: "true"')
    out, _ = _assess(
        _routes(
            **{
                f"contents/{REVIEW_PATH}?ref={MAIN}": _content(quoted, "w1"),
                f"contents/{REVIEW_PATH}?ref={HEAD}": _content(quoted, "w1"),
                "issues/7/comments?per_page=100": [],
            }
        )
    )
    assert out.state == cs.FAILED
    assert "did not review" in out.verdict()


def test_renaming_the_review_workflow_away_is_an_edit_to_it():
    renamed = [{"filename": ".github/workflows/review.yml", "previous_filename": REVIEW_PATH}]
    out, _ = _assess(_routes(**{"pulls/7/files?per_page=100": renamed}))
    assert "review it by hand" in out.verdict()


def test_inline_comments_from_a_reviewer_under_its_own_app_name_are_counted():
    inline = [{"user": {"login": "offworld-claude[bot]", "type": "Bot"}, "original_commit_id": HEAD}]
    out, _ = _assess(_routes(**{"pulls/7/comments?per_page=100": inline}))
    assert "with 1 inline comment(s) made on this head" in _text(out)


def test_no_review_also_drops_the_review_run_from_the_gate():
    out, _ = _assess(
        _routes(**{"actions/runs/2/attempts/1/jobs?per_page=100": _jobs(("claude-review", "failure"))}),
        review=False,
    )
    assert out.state == cs.GREEN, _text(out)


def test_the_pr_file_list_is_read_once_per_head_and_base(monkeypatch):
    calls = []

    def gh(args):
        calls.append(args)
        return '{"filename": "a.py"}'

    monkeypatch.setattr(cs, "_gh", gh)
    github = cs.GitHub()
    for version in ("h1..b1", "h1..b1", "h2..b1"):
        github.items("repos/o/r/pulls/7/files?per_page=100", fixed=True, version=version)
    assert len(calls) == 2


def test_the_pr_file_list_is_kept_only_for_the_head_and_base_it_was_read_at():
    _, gh = _assess(_routes())
    assert gh.fixed_versions[f"repos/{REPO}/pulls/7/files?per_page=100"] == f"{HEAD}..{'c' * 40}"


def _watched(out, seconds):
    """What --watch makes of `out` after seeing it unchanged for `seconds`."""
    seen = {}
    cs.escalate(out, seen, 0.0)
    cs.escalate(out, seen, float(seconds))
    return out


def test_a_review_workflow_that_never_triggered_is_pending_then_final_under_watch():
    out, _ = _assess(_routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": [_run(1)]}))
    assert out.state == cs.PENDING
    assert _watched(out, cs.REVIEW_GRACE_S).state == cs.FAILED
    assert "did not trigger" in out.verdict()


def test_runs_that_all_skipped_every_job_are_pending_then_final_under_watch():
    runs = [_run(1), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "skipped")),
                "actions/runs/2/attempts/1/jobs?per_page=100": _jobs(("claude-review", "skipped")),
            }
        )
    )
    assert out.state == cs.PENDING
    assert _watched(out, cs.ALL_SKIPPED_GRACE_S).state == cs.FAILED
    assert "nothing was tested" in out.verdict()


def test_a_commit_no_workflow_picked_up_is_pending_then_final_under_watch():
    out, _ = _assess(_routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": []}))
    assert out.state == cs.PENDING
    assert _watched(out, cs.NO_RUNS_GRACE_S).state == cs.FAILED
    assert "no workflow ran for this commit" in out.verdict()


def test_a_wait_shorter_than_its_grace_stays_pending():
    out, _ = _assess(_routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": []}), review=False)
    assert _watched(out, cs.NO_RUNS_GRACE_S - 1).state == cs.PENDING


def test_a_wait_that_clears_starts_again_from_nothing():
    seen = {}
    first, _ = _assess(_routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": []}))
    cs.escalate(first, seen, 0.0)
    cleared, _ = _assess(_routes())
    cs.escalate(cleared, seen, 100.0)
    again, _ = _assess(_routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": []}))
    cs.escalate(again, seen, float(cs.NO_RUNS_GRACE_S))
    assert again.state == cs.PENDING


def test_a_merged_pr_is_not_told_to_rebase_when_main_s_review_workflow_moved_on():
    out, _ = _assess(
        _routes(
            **{
                "pulls/7": _pr(state="closed", merged=True),
                f"contents/{REVIEW_PATH}?ref={HEAD}": _content(TRACKED, "w0"),
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert "differs" not in _text(out)


def _stale_untracked(moved):
    routes = _routes(
        **{
            f"contents/{REVIEW_PATH}?ref={MAIN}": _content(UNTRACKED, "w1"),
            f"contents/{REVIEW_PATH}?ref={HEAD}": _content(UNTRACKED, "w0"),
            "issues/7/comments?per_page=100": [],
        }
    )
    if moved:
        commit, pulls = _change("d" * 40, T2)
        routes[HISTORY] = [commit]
        routes.update(pulls)
    return _assess(routes)[0]


def test_an_untracked_review_stays_neutral_when_main_s_copy_moved_after_it_ran():
    out = _stale_untracked(moved=True)
    assert out.state == cs.GREEN, _text(out)
    assert "does not track progress" in _text(out)


def test_a_stale_head_whose_review_run_finished_is_still_unreviewed():
    out = _stale_untracked(moved=False)
    assert out.state == cs.FAILED
    assert "rebase" in out.verdict()


def test_a_review_run_that_reads_completed_with_its_job_going_is_not_judged_yet():
    out, _ = _assess(
        _routes(
            **{
                "actions/runs/2/attempts/1/jobs?per_page=100": _jobs(("claude-review", None)),
                "issues/7/comments?per_page=100": [_comment(2, ticked=False)],
            }
        )
    )
    assert out.state == cs.PENDING, _text(out)


@pytest.mark.parametrize(("state", "code"), [(cs.GREEN, 0), (cs.FAILED, 1), (cs.PENDING, 3)])
def test_exit_codes(state, code):
    assert cs.EXIT[state] == code


def test_a_pr_and_a_commit_together_are_refused():
    with pytest.raises(SystemExit) as exited:
        cs.main(["7", "--commit", "main", "-R", REPO])
    assert exited.value.code == 2


def test_a_failing_check_from_another_app_fails_and_actions_checks_are_not_counted_twice():
    checks = [
        {"name": "codecov/patch", "status": "completed", "conclusion": "failure", "app": {"slug": "codecov"}},
        {"name": "tests", "status": "completed", "conclusion": "failure", "app": {"slug": "github-actions"}},
    ]
    out, _ = _assess(_routes(**{f"commits/{HEAD}/check-runs?per_page=100": checks}))
    assert out.state == cs.FAILED
    assert "codecov/patch (codecov) failure" in out.verdict()
    assert "tests (github-actions)" not in out.verdict()


def test_a_pending_commit_status_is_pending():
    status = [{"context": "ci/external", "state": "pending"}]
    out, _ = _assess(_routes(**{f"commits/{HEAD}/status?per_page=100": status}))
    assert out.state == cs.PENDING
    assert "ci/external pending" in out.verdict()


@pytest.mark.parametrize(
    ("answer", "finished"),
    [("", True), ('{"name": "setup", "status": "completed", "conclusion": "success"}', False)],
    ids=["no jobs listed yet", "run still going"],
)
def test_a_job_list_that_may_still_grow_is_read_again(monkeypatch, answer, finished):
    calls = []

    def gh(args):
        calls.append(args)
        return answer

    monkeypatch.setattr(cs, "_gh", gh)
    github = cs.GitHub()
    cs.attempt_jobs(github, REPO, 1, 1, finished=finished)
    cs.attempt_jobs(github, REPO, 1, 1, finished=finished)
    assert len(calls) == 2


@pytest.mark.parametrize(
    ("stderr", "transient"),
    [
        ('no pull requests found for branch "feat/geofence-alerts"', False),
        ('no pull requests found for branch "fix/reconnect"', False),
        ("gh: Not Found (HTTP 404)", False),
        ("HTTP 502: Bad Gateway", True),
        ("API rate limit exceeded (HTTP 403)", True),
        ("error connecting to api.github.com", True),
        ('Get "https://api.github.com/x": dial tcp 140.82.1.1:443: i/o timeout', True),
        ("net/http: TLS handshake timeout", True),
        ("connect: network is unreachable", True),
    ],
)
def test_only_an_outage_is_transient(stderr, transient):
    assert cs.GhError(["api"], stderr).transient is transient


@pytest.mark.parametrize("spelling", ["false", "False", "no", "off", "'false'"])
def test_every_yaml_spelling_of_false_turns_tracking_off(spelling):
    off = TRACKED.replace("track_progress: true", f"track_progress: {spelling}")
    out, _ = _assess(
        _routes(
            **{
                f"contents/{REVIEW_PATH}?ref={MAIN}": _content(off, "w1"),
                f"contents/{REVIEW_PATH}?ref={HEAD}": _content(off, "w1"),
                "issues/7/comments?per_page=100": [],
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)


def test_a_missing_gh_is_no_verdict_rather_than_a_bad_question(monkeypatch):
    def missing(*args, **kwargs):
        raise FileNotFoundError("gh")

    monkeypatch.setattr(cs.subprocess, "run", missing)
    with pytest.raises(SystemExit) as exited:
        cs._gh(["api", "user"])
    assert exited.value.code == 4


def test_runs_another_pr_on_the_same_head_started_do_not_count():
    other = {**_run(9, at=T2), "pull_requests": [{"number": 8}]}
    mine = {**_run(1, at=T1, conclusion="failure"), "pull_requests": [{"number": 7}]}
    out, gh = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": [other, mine, _run(2, "Claude Code Review")],
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "failure")),
            }
        )
    )
    assert out.state == cs.FAILED
    assert f"repos/{REPO}/actions/runs/9/attempts/1/jobs?per_page=100" not in gh.calls


def test_a_wait_restarts_when_the_head_moves():
    seen = {}
    first, _ = _assess(_routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": []}), review=False)
    cs.escalate(first, seen, 0.0)
    moved = _pr(head={"sha": OLD, "ref": "feat/x", "repo": {"full_name": REPO}})
    routes = _routes(**{"pulls/7": moved, f"actions/runs?head_sha={OLD}&per_page=100": []})
    routes[f"repos/{REPO}/git/ref/heads/feat/x"] = {"object": {"sha": OLD}}
    routes[f"repos/{REPO}/commits/{OLD}/check-runs?per_page=100"] = []
    routes[f"repos/{REPO}/commits/{OLD}/status?per_page=100"] = []
    second, _ = _assess(routes, review=False)
    cs.escalate(second, seen, float(cs.NO_RUNS_GRACE_S))
    assert second.state == cs.PENDING


def test_no_review_does_not_read_the_review_run_at_all():
    _, gh = _assess(_routes(), review=False)
    assert f"repos/{REPO}/actions/runs/2/attempts/1/jobs?per_page=100" not in gh.calls


def test_a_watch_rides_out_a_blip_on_its_first_reading(monkeypatch):
    readings = iter([cs.GhError(["api"], "HTTP 502: Bad Gateway"), cs.Assessment(head=HEAD)])

    def assess_pr(*args, **kwargs):
        answer = next(readings)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(cs, "assess_pr", assess_pr)
    monkeypatch.setattr(cs.time, "sleep", lambda s: None)
    assert cs.main(["7", "-R", REPO, "--watch"]) == 0


def test_a_single_reading_does_not_retry_a_blip(monkeypatch):
    calls = []

    def assess_pr(*args, **kwargs):
        calls.append(args)
        raise cs.GhError(["api"], "HTTP 502: Bad Gateway")

    monkeypatch.setattr(cs, "assess_pr", assess_pr)
    monkeypatch.setattr(cs.time, "sleep", lambda s: None)
    assert cs.main(["7", "-R", REPO]) == 4
    assert len(calls) == 1


def test_a_change_merged_after_the_run_began_counts_though_its_commit_is_older():
    routes = _routes(
        **{
            f"contents/{REVIEW_PATH}?ref={MAIN}": _content(UNTRACKED, "w1"),
            f"contents/{REVIEW_PATH}?ref={HEAD}": _content(UNTRACKED, "w0"),
            "issues/7/comments?per_page=100": [],
        }
    )
    commit, pulls = _change("e" * 40, T0, merged_at=T2)
    routes[HISTORY] = [commit]
    routes.update(pulls)
    out, _ = _assess(routes)
    assert out.state == cs.GREEN, _text(out)


def test_a_review_that_ran_does_not_stand_in_for_ci_that_skipped_everything():
    out, _ = _assess(
        _routes(**{"actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "skipped"), ("deploy", "skipped"))})
    )
    assert out.state == cs.PENDING
    assert _watched(out, cs.ALL_SKIPPED_GRACE_S).state == cs.FAILED
    assert "nothing was tested" in out.verdict()


def test_a_review_that_ran_does_not_stand_in_for_ci_that_never_registered():
    out, _ = _assess(_routes(**{f"actions/runs?head_sha={HEAD}&per_page=100": [_run(2, "Claude Code Review")]}))
    assert out.state == cs.PENDING
    assert "no runs yet" in out.verdict()


def test_a_review_still_going_is_not_failed_when_main_s_copy_moved_after_it_began():
    commit, pulls = _change("f" * 40, T2)
    routes = _routes(
        **{
            "actions/runs/2/attempts/1/jobs?per_page=100": _jobs(("claude-review", None)),
            f"contents/{REVIEW_PATH}?ref={HEAD}": _content(TRACKED, "w0"),
            HISTORY: [commit],
        }
    )
    routes.update(pulls)
    out, _ = _assess(routes)
    assert out.state == cs.PENDING, _text(out)


def test_the_comment_of_the_run_that_lent_the_review_its_job_counts():
    runs = [_run(1), _run(12, "Claude Code Review", at=T2), _run(2, "Claude Code Review", at=T1)]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/12/attempts/1/jobs?per_page=100": _jobs(
                    ("gate", "success"), ("claude-review", "skipped")
                ),
                "actions/runs/2/attempts/1/jobs?per_page=100": _jobs(("gate", "success"), ("claude-review", "success")),
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)


def test_track_progress_set_by_an_expression_is_read_as_untracked():
    expr = TRACKED.replace("track_progress: true", "track_progress: ${{ github.event_name == 'issue_comment' }}")
    out, _ = _assess(
        _routes(
            **{
                f"contents/{REVIEW_PATH}?ref={MAIN}": _content(expr, "w1"),
                f"contents/{REVIEW_PATH}?ref={HEAD}": _content(expr, "w1"),
                "issues/7/comments?per_page=100": [],
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert "by an expression" in _text(out)


def test_a_partial_review_names_the_rerun_that_works_when_no_job_failed():
    out, _ = _assess(_routes(**{"issues/7/comments?per_page=100": [_comment(2, ticked=False)]}))
    assert "gh run rerun 2" in out.verdict()
    assert "--failed" not in out.verdict()


def test_a_missing_git_leaves_the_local_branch_unread(monkeypatch):
    def missing(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(cs.subprocess, "run", missing)
    assert cs.local_tip(REPO, "feat/x", HEAD) == (None, "unknown")


def test_a_failure_its_run_allows_does_not_gate():
    out, _ = _assess(
        _routes(**{"actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "success"), ("nightly", "failure"))})
    )
    assert out.state == cs.GREEN, _text(out)
    assert "nightly failed, which its run allows" in _text(out)


def test_a_failure_in_a_run_that_failed_still_gates():
    runs = [_run(1, conclusion="failure"), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "success"), ("nightly", "failure")),
            }
        )
    )
    assert out.state == cs.FAILED


CIRCLE = [{"name": "ci/circle", "status": "completed", "conclusion": "success", "app": {"slug": "circleci"}}]
WORKFLOWS = "actions/workflows?per_page=100"


def _workflow(path, state="active"):
    return {"path": path, "state": state}


def test_checks_from_another_app_count_as_ci_where_actions_runs_none():
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": [_run(2, "Claude Code Review")],
                f"commits/{HEAD}/check-runs?per_page=100": CIRCLE,
                WORKFLOWS: [_workflow(REVIEW_PATH), _workflow("dynamic/github-code-scanning/codeql")],
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)


def test_another_app_s_check_does_not_stand_in_for_actions_ci_not_yet_registered():
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": [_run(2, "Claude Code Review")],
                f"commits/{HEAD}/check-runs?per_page=100": CIRCLE,
                WORKFLOWS: [_workflow(REVIEW_PATH), _workflow(".github/workflows/ci.yml")],
            }
        )
    )
    assert out.state == cs.PENDING
    assert "no runs yet" in out.verdict()


def test_push_runs_from_another_branch_at_the_same_commit_do_not_count():
    elsewhere = {**_run(9, event="push", conclusion="failure", at=T2), "head_branch": "feat/y"}
    mine = {**_run(8, event="push", at=T1), "head_branch": "feat/x"}
    out, gh = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": [elsewhere, mine, _run(1), _run(2, "Claude Code Review")],
                "actions/runs/8/attempts/1/jobs?per_page=100": _jobs(("tests", "success")),
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert f"repos/{REPO}/actions/runs/9/attempts/1/jobs?per_page=100" not in gh.calls


def test_an_inline_comment_after_track_progress_false_is_not_part_of_the_value():
    off = TRACKED.replace("track_progress: true", "track_progress: false  # too noisy")
    out, _ = _assess(
        _routes(
            **{
                f"contents/{REVIEW_PATH}?ref={MAIN}": _content(off, "w1"),
                f"contents/{REVIEW_PATH}?ref={HEAD}": _content(off, "w1"),
                "issues/7/comments?per_page=100": [],
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)


def test_the_default_branch_s_copy_is_read_by_commit_so_a_watch_reads_it_once():
    _, gh = _assess(_routes())
    assert f"repos/{REPO}/contents/{REVIEW_PATH}?ref=main" not in gh.calls
    assert f"repos/{REPO}/contents/{REVIEW_PATH}?ref={MAIN}" in gh.calls


def test_a_lent_failure_its_own_run_allowed_does_not_gate():
    runs = [_run(3, at=T2), _run(1, at=T1), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/3/attempts/1/jobs?per_page=100": _jobs(("tests", "success"), ("nightly", "skipped")),
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "success"), ("nightly", "failure")),
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert "nightly failed, which its run allows" in _text(out)


def test_a_failure_in_a_run_still_going_gates():
    runs = [_run(1, status="in_progress", conclusion=None), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "failure"), ("lint", None)),
            }
        )
    )
    assert out.state == cs.FAILED


def test_a_repo_named_without_a_pr_is_a_usage_error(monkeypatch):
    # The current branch's PR belongs to this directory's repo, not the one named.
    asked = []
    monkeypatch.setattr(cs, "_gh", lambda args: asked.append(args) or "602")
    monkeypatch.setattr(cs, "assess_pr", lambda *a, **k: cs.Assessment(head=HEAD))
    with pytest.raises(SystemExit) as exited:
        cs.main(["-R", REPO])
    assert exited.value.code == 2
    assert asked == []


def test_a_local_branch_with_unpushed_commits_fails_the_reading():
    out, _ = _assess(_routes(), local=OLD, standing="ahead")
    assert out.state == cs.FAILED
    assert "push" in out.verdict()


def test_a_pushed_commit_the_pr_head_has_not_followed_is_a_wait_not_unpushed_work():
    out, _ = _assess(_routes(**{"git/ref/heads/feat/x": {"object": {"sha": OLD}}}), local=OLD, standing="ahead")
    assert out.state == cs.PENDING, _text(out)
    assert "force-with-lease" in out.verdict()


def test_a_local_branch_a_remote_rebase_superseded_is_noted_not_failed():
    out, _ = _assess(_routes(), local=OLD, standing="superseded")
    assert out.state == cs.GREEN, _text(out)
    assert "superseded" in _text(out)


def test_a_local_branch_diverged_with_work_the_head_lacks_fails():
    out, _ = _assess(_routes(), local=OLD, standing="diverged")
    assert out.state == cs.FAILED
    assert "reconcile" in out.verdict()


def test_a_head_that_lags_its_branch_is_not_judged_by_its_old_ci():
    out, _ = _assess(
        _routes(
            **{
                "git/ref/heads/feat/x": {"object": {"sha": OLD}},
                f"actions/runs?head_sha={HEAD}&per_page=100": [
                    _run(1, conclusion="failure"),
                    _run(2, "Claude Code Review"),
                ],
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("tests", "failure")),
            }
        )
    )
    assert out.state == cs.PENDING, _text(out)
    assert "tests failure" not in out.verdict()


def test_a_review_comment_with_no_checklist_is_not_a_review():
    bare = _comment(2)
    bare["body"] = "**Claude finished** [View job](https://github.com/org/app/actions/runs/2)\n\nWorking..."
    out, _ = _assess(_routes(**{"issues/7/comments?per_page=100": [bare]}))
    assert out.state == cs.FAILED
    assert "no checklist" in out.verdict()


@pytest.mark.parametrize("gap", ["\n", "  - a note on the first step\n"])
def test_an_unticked_step_after_a_blank_line_or_sub_item_is_seen(gap):
    body = (
        "**Claude finished** [View job](https://github.com/org/app/actions/runs/2)\n\n"
        f"- [x] Gather context\n{gap}- [ ] Post findings\n\nFindings:\n\n- [ ] Add a test\n"
    )
    comment = {**_comment(2), "body": body}
    out, _ = _assess(_routes(**{"issues/7/comments?per_page=100": [comment]}))
    assert out.state == cs.FAILED
    assert "Post findings" in _text(out)
    assert "Add a test" not in _text(out)


def test_the_local_branch_is_placed_against_the_head_by_real_git(tmp_path, monkeypatch):
    def git(*args):
        done = subprocess.run(["git", *args], cwd=tmp_path, capture_output=True, text=True, check=True)
        return done.stdout.strip()

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.test")
    git("config", "user.name", "t")
    git("remote", "add", "origin", f"git@github.com:{REPO}.git")
    git("commit", "-q", "--allow-empty", "-m", "a")
    first = git("rev-parse", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "b")
    second = git("rev-parse", "HEAD")
    git("checkout", "-q", "-b", "other", first)
    git("branch", "-q", "feat/x", second)
    monkeypatch.chdir(tmp_path)

    assert cs.local_tip(REPO, "feat/x", first) == (second, "ahead")
    git("branch", "-q", "-f", "feat/x", first)
    assert cs.local_tip(REPO, "feat/x", second) == (first, "behind")
    assert cs.local_tip(REPO, "feat/x", "f" * 40) == (first, "unknown")
    assert cs.local_tip("org/elsewhere", "feat/x", second) == (None, "unknown")
    # The branch was at `second` here and was then amended: unpushed work, not a rewrite elsewhere.
    git("checkout", "-q", "feat/x")
    git("reset", "-q", "--hard", second)
    git("commit", "-q", "--amend", "--allow-empty", "-m", "b, amended")
    amended = git("rev-parse", "HEAD")
    assert cs.local_tip(REPO, "feat/x", second) == (amended, "rewritten")


def test_diverged_work_is_told_from_a_branch_a_remote_rebase_superseded(tmp_path, monkeypatch):
    def git(*args):
        done = subprocess.run(["git", *args], cwd=tmp_path, capture_output=True, text=True, check=True)
        return done.stdout.strip()

    def commit(name, text):
        (tmp_path / name).write_text(text)
        git("add", name)
        git("commit", "-q", "-m", name)
        return git("rev-parse", "HEAD")

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.test")
    git("config", "user.name", "t")
    git("remote", "add", "origin", f"git@github.com:{REPO}.git")
    base = commit("a", "a")
    git("checkout", "-q", "-b", "feat/x")
    mine = commit("b", "b")
    # Elsewhere, the head was rebased onto a newer main: b again, on top of c.
    git("checkout", "-q", "-b", "remote", base)
    commit("c", "c")
    git("cherry-pick", mine)
    rebased = git("rev-parse", "HEAD")
    # And elsewhere again, a head built on a's successor that lacks b entirely.
    git("checkout", "-q", "-b", "other", base)
    other = commit("d", "d")
    monkeypatch.chdir(tmp_path)

    assert cs.local_tip(REPO, "feat/x", rebased) == (mine, "superseded")
    assert cs.local_tip(REPO, "feat/x", other) == (mine, "diverged")


def test_a_branch_amended_here_and_not_pushed_fails_the_reading():
    out, _ = _assess(_routes(), local=OLD, standing="rewritten")
    assert out.state == cs.FAILED
    assert "push" in out.verdict()


def test_a_skipped_matrix_job_is_lent_every_expansion_that_ran():
    # As GitHub lists them: an edit's run names a skipped matrix job once, unexpanded.
    web = "Web (${{ (matrix.label || matrix.workspace) }})"
    runs = [_run(3, at=T2), _run(1, at=T1, conclusion="failure"), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/3/attempts/1/jobs?per_page=100": _jobs(
                    ("contract", "success"), ("backend-tests", "skipped"), (web, "skipped")
                ),
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(
                    ("contract", "success"),
                    ("backend-tests (1)", "success"),
                    ("backend-tests (2)", "failure"),
                    ("Web (e2e)", "success"),
                    ("Web (dashboard tests 1/2)", "failure"),
                ),
            }
        )
    )
    assert out.state == cs.FAILED
    assert "backend-tests (2) failure" in out.verdict()
    assert "Web (dashboard tests 1/2) failure" in out.verdict()
    assert "${{" not in out.verdict()


@pytest.mark.parametrize(
    ("skipped", "ran", "same"),
    [
        ("lint", "lint", True),
        ("lint", "lint-extra", False),
        ("backend-tests", "backend-tests (3)", True),
        ("Web (${{ matrix.label }})", "Web (e2e)", True),
        ("Web (${{ matrix.label }})", "Webhooks (e2e)", False),
        ("Web (e2e)", "Web (dashboard)", False),
    ],
)
def test_matrix_names_match_their_expansions_only(skipped, ran, same):
    assert cs._same_job(skipped, ran) is same


def test_a_rerun_in_a_run_that_lends_jobs_is_still_listed():
    runs = [_run(3, at=T2), _run(1, at=T1, attempt=2), _run(2, "Claude Code Review")]
    out, _ = _assess(
        _routes(
            **{
                f"actions/runs?head_sha={HEAD}&per_page=100": runs,
                "actions/runs/3/attempts/1/jobs?per_page=100": _jobs(("contract", "success"), ("tests", "skipped")),
                "actions/runs/1/attempts/2/jobs?per_page=100": _jobs(("contract", "success"), ("tests", "success")),
                "actions/runs/1/attempts/1": {"conclusion": "failure"},
                "actions/runs/1/attempts/1/jobs?per_page=100": _jobs(("contract", "success"), ("tests", "failure")),
            }
        )
    )
    assert out.state == cs.GREEN, _text(out)
    assert "run 1's attempt 1 was failure: tests" in _text(out)


def test_a_pushed_diverged_tip_the_pr_head_has_not_followed_is_a_wait():
    out, _ = _assess(_routes(**{"git/ref/heads/feat/x": {"object": {"sha": OLD}}}), local=OLD, standing="diverged")
    assert out.state == cs.PENDING, _text(out)


def test_a_fork_s_branch_is_not_compared_with_a_local_branch_of_the_same_name():
    seen = []
    fork = _pr(head={"sha": HEAD, "ref": "main", "repo": {"full_name": "someone/app"}})
    routes = _routes(**{"pulls/7": fork})
    routes["repos/someone/app/git/ref/heads/main"] = {"object": {"sha": HEAD}}
    gh = FakeGitHub(routes)
    out = cs.assess_pr(
        gh, REPO, 7, local=lambda repo, ref, head: seen.append(ref) or (OLD, "diverged"), sleep=lambda s: None
    )
    assert out.state == cs.GREEN, _text(out)
    assert seen == []
