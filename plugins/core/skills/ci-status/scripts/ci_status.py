#!/usr/bin/env python3
"""Report a pull request's real CI state, and exit non-zero unless every gate passed.

    ci_status.py [PR] [-R owner/repo] [--watch] [--no-review] [-v]
    ci_status.py --commit SHA [-R owner/repo] [--watch] [-v]

`gh pr checks` and `gh run watch` answer a narrower question than they appear to,
and each of these has passed for green:

* Just after a push, no run is registered yet, and `gh pr checks --watch` prints
  "no checks reported" and exits 0. Here that is "not settled", never a pass.
* A PR whose branch conflicts has no merge ref, so pull_request CI never runs.
  That is reported as a failure, since nothing will change until a rebase.
* GitHub can move a branch without moving the PR's head, so no CI runs for the
  new commit. While the head lags its branch nothing about the old head is
  judged. A local branch with unpushed work (new commits, or an amend or rebase
  of the PR's head) fails the reading, as none of it describes that work, and so
  does one that has diverged from the head with commits the head has no copy of.
  A head this clone has not fetched cannot be compared, and is only noted.
* A title or body edit fires an `edited` run in which every job skips, and
  `gh pr checks` then shows those skips in place of the real results. Runs whose
  jobs all skipped are set aside.
* After a force-push the watchers can report the runs the push superseded. Only
  runs for the head SHA count, and of several for one workflow (a stack
  force-push queues two, and cancels one), the newest that was not cancelled.
* `gh run watch --exit-status` has exited 0 on a failed run, and a run can read
  completed while its jobs are still going. Each job's own conclusion decides.
* A rerun replaces a run's conclusion, so a failure that was rerun reads as a
  pass. The latest attempt decides, and earlier failed attempts are listed.
* The Claude review skips itself on a PR that edits its own workflow, and on a
  branch carrying an older copy of that workflow than the default branch, and
  says nothing either way. A review counts only when a bot comment posted during
  the latest attempt of this head's review run links back to it, carrying a
  progress checklist with every item ticked. Where the review workflow does not
  track progress it posts nothing to link, so there a finished run is all there
  is to read, and ci-status says so rather than calling it reviewed.
* One commit can head two branches, each with its own PR, and their runs share
  its SHA. Only this PR's pull_request runs, and push runs on its branch, count.
  GitHub ties a run to every PR open from the same branch, though, so two PRs
  from one branch cannot be told apart.

Something that may yet arrive (a run, a review run, the PR's head following its
branch) is "not settled" in a single reading, because GitHub records no push
time to judge the wait against. --watch calls it final once it has seen it last
a few minutes.

A job allowed to fail (continue-on-error) is listed but does not gate, which
GitHub shows as a failed job in a run that succeeded; until its run finishes it
cannot be told from a real failure, and gates. pull_request_target runs
are filed under the base branch's commit, so they are not read.

Checks posted by other apps, and commit statuses, count as gates too. Check runs
the github-actions app posts are taken to mirror jobs and are not read twice, so a
check a workflow posts through the Checks API (a test reporter) is not counted. A
workflow_run-triggered run counts once it has registered, but nothing waits for
one that has not.

Exit status: 0 green; 1 failed, or will not run until someone acts; 2 the
question was wrong (bad arguments, or GitHub refused them); 3 not settled yet;
4 GitHub could not be read.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import time
import urllib.parse
from collections.abc import Callable
from dataclasses import dataclass, field

GREEN, FAILED, PENDING = "green", "failed", "pending"
EXIT = {GREEN: 0, FAILED: 1, PENDING: 3}
EXIT_UNREADABLE = 4

# Events whose runs gate a change. workflow_dispatch and schedule runs share the
# SHA but test something else; issue_comment runs carry the default branch's SHA.
GATE_EVENTS = {"pull_request", "pull_request_target", "push", "merge_group", "workflow_run"}
PR_EVENTS = {"pull_request", "pull_request_target"}
BAD_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required", "startup_failure", "stale"}

REVIEW_WORKFLOW = "claude-code-review.yml"
REVIEW_PATH = f".github/workflows/{REVIEW_WORKFLOW}"

# How long --watch waits on a condition before calling it final. Timed from
# when the watch first saw it, since GitHub records no push time to time it from.
STUCK_GRACE_S = 180  # a branch ahead of its PR's head
NO_RUNS_GRACE_S = 600  # no run for the commit at all
ALL_SKIPPED_GRACE_S = 180  # only runs that skipped every job
REVIEW_GRACE_S = 300  # no review run for the head
# Consecutive unreadable polls --watch rides out before giving up.
WATCH_ERRORS = 5


class GhError(Exception):
    def __init__(self, args: list[str], stderr: str):
        super().__init__(f"gh {' '.join(args)}: {stderr.strip()}")
        self.not_found = "HTTP 404" in stderr
        # An outage, a rate limit or a timeout, as against a question with no answer.
        self.transient = bool(
            re.search(
                r"HTTP (5\d\d|429)\b|timed out|rate limit|error connecting|connection (refused|reset)|unexpected EOF"
                r"|i/o timeout|handshake timeout|network is unreachable|deadline exceeded|broken pipe",
                stderr,
                re.IGNORECASE,
            )
        )


def _gh(args: list[str]) -> str:
    try:
        done = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=120, check=False)
    except FileNotFoundError:
        print("ci-status needs the GitHub CLI, gh, on PATH, so there is no verdict", file=sys.stderr)
        raise SystemExit(EXIT_UNREADABLE) from None
    except subprocess.TimeoutExpired as exc:
        raise GhError(args, "timed out after 120s") from exc
    if done.returncode != 0:
        raise GhError(args, done.stderr)
    return done.stdout


class GitHub:
    """The REST calls ci-status makes, through gh so its authentication applies.

    `fixed` marks an answer that cannot change (a finished attempt's jobs, a file
    at a commit), which --watch then reads once rather than on every poll. It is
    True, or a test the answer must pass before it is kept.
    """

    def __init__(self):
        self._fixed: dict[tuple[str, str], object] = {}

    def get(self, path: str, *, fixed: bool | Callable[[object], bool] = False):
        return self._read(path, "", fixed, lambda: json.loads(_gh(["api", path])))

    def items(
        self, path: str, key: str | None = None, *, fixed: bool | Callable[[object], bool] = False, version: str = ""
    ) -> list:
        def read():
            jq = f".{key}[] | @json" if key else ".[] | @json"
            out = _gh(["api", "--paginate", path, "--jq", jq])
            return [json.loads(line) for line in out.splitlines() if line.strip()]

        return self._read(path, f"{key}@{version}", fixed, read)

    def _read(self, path, key, fixed, read):
        if (path, key) in self._fixed:
            return self._fixed[(path, key)]
        answer = read()
        if fixed is True or (callable(fixed) and fixed(answer)):
            self._fixed[(path, key)] = answer
        return answer


@dataclass
class Job:
    name: str
    status: str
    conclusion: str | None
    # The older run this job's result comes from, when the deciding run skipped it.
    source: int | None = None
    # A lent job's failure that its own run finished as a success, so allowed it.
    allowed: bool = False
    # Whether its `if:` let it queue. A run cancelled early lists the jobs GitHub had not
    # yet evaluated as cancelled with no runner at all; a queued job has runner_id 0.
    queued: bool = True

    @property
    def state(self) -> str:
        return _state(self.status, self.conclusion)


def _state(status: str | None, conclusion: str | None) -> str:
    return (conclusion if status == "completed" else status) or "?"


@dataclass
class Run:
    id: int
    name: str
    path: str
    event: str
    status: str
    conclusion: str | None
    attempt: int
    created_at: str
    started_at: str
    jobs: list[Job] = field(default_factory=list)
    # Older runs of the same workflow whose jobs this one carries, having skipped them.
    lenders: list[Run] = field(default_factory=list)

    @property
    def is_review(self) -> bool:
        return self.path.rsplit("/", 1)[-1] == REVIEW_WORKFLOW

    @property
    def all_skipped(self) -> bool:
        if self.status != "completed":
            return False
        if not self.jobs:
            return self.conclusion == "skipped"
        return all(job.state == "skipped" for job in self.jobs)


@dataclass
class Assessment:
    lines: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)
    # The commit judged. A wait belongs to it, so a push restarts every wait.
    head: str = ""
    # Pending conditions that stop being worth waiting for: key -> (seconds, failure).
    waits: dict[str, tuple[float, str]] = field(default_factory=dict)

    def wait(self, key: str, grace: float, pending: str, failure: str) -> None:
        """Pending now; --watch turns it into `failure` once it has lasted `grace` seconds."""
        self.pending.append(pending)
        self.waits[f"{key}@{self.head}"] = (grace, failure)

    @property
    def state(self) -> str:
        if self.failures:
            return FAILED
        return PENDING if self.pending else GREEN

    def say(self, label: str, text: str) -> None:
        first, *rest = text.splitlines() or [""]
        self.lines.append(f"  {label:<10}{first}")
        self.lines.extend(f"  {'':<10}{line}" for line in rest)

    def verdict(self) -> str:
        if self.failures:
            return "FAILED: " + "; ".join(self.failures)
        if self.pending:
            return "PENDING: " + "; ".join(self.pending)
        return "GREEN: every gate passed"


def fetch_runs(
    gh: GitHub, repo: str, sha: str, *, pr: int | None = None, branch: str | None = None, review: bool = True
) -> list[Run]:
    runs = []
    for raw in gh.items(f"repos/{repo}/actions/runs?head_sha={sha}&per_page=100", "workflow_runs"):
        # A fork's pull_request run lists no PRs at all, so an empty list is kept.
        prs = [p.get("number") for p in raw.get("pull_requests") or []]
        if pr is not None and raw["event"] in PR_EVENTS and prs and pr not in prs:
            continue
        if branch is not None and raw["event"] == "push" and raw.get("head_branch") != branch:
            continue
        run = Run(
            id=raw["id"],
            name=raw.get("name") or raw.get("path", "?"),
            path=raw.get("path") or "",
            event=raw["event"],
            status=raw["status"],
            conclusion=raw.get("conclusion"),
            attempt=raw.get("run_attempt") or 1,
            created_at=raw.get("created_at") or "",
            started_at=raw.get("run_started_at") or raw.get("created_at") or "",
        )
        if run.is_review and not review:
            continue
        if run.event in GATE_EVENTS:
            run.jobs = attempt_jobs(gh, repo, run.id, run.attempt, finished=run.status == "completed")
        runs.append(run)
    return runs


def attempt_jobs(gh: GitHub, repo: str, run_id: int, attempt: int, *, finished: bool) -> list[Job]:
    # A run can read completed while its jobs are still going, and a queued run
    # lists none yet, so a list is kept only once the run and every job in it
    # have finished.
    jobs = gh.items(
        f"repos/{repo}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100",
        "jobs",
        fixed=lambda answer: finished and bool(answer) and all(j.get("status") == "completed" for j in answer),
    )
    return [
        Job(j["name"], j["status"], j.get("conclusion"), queued=bool(j.get("steps")) or j.get("runner_id") is not None)
        for j in jobs
    ]


def choose_runs(runs: list[Run]) -> tuple[list[Run], list[tuple[Run, str]]]:
    """The run that decides each workflow, and every other run with why it was set aside."""
    ignored: list[tuple[Run, str]] = []
    groups: dict[tuple[str, str], list[Run]] = {}
    for run in runs:
        if run.event not in GATE_EVENTS:
            ignored.append((run, f"a {run.event} run, not a gate"))
        elif run.all_skipped:
            ignored.append((run, "every job skipped (the run a title or body edit fires)"))
        else:
            groups.setdefault((run.path or run.name, run.event), []).append(run)
    chosen = []
    for group in groups.values():
        group.sort(key=lambda r: (r.created_at, r.id), reverse=True)
        live = [r for r in group if r.conclusion != "cancelled"]
        pick = live[0] if live else group[0]
        # A cancelled run lends only what no live run ran: a job it cut short (a
        # timeout, a hand cancel) must not vanish behind an edit's run that skipped it.
        cancelled = [r for r in group if r.conclusion == "cancelled" and r is not pick]
        donors = _fill_skipped(pick, [r for r in live if r is not pick] + cancelled)
        pick.lenders = [r for r in group if r.id in donors]
        chosen.append(pick)
        for other in group:
            if other is not pick:
                lent = ", which lends it the jobs it skipped" if other.id in donors else ""
                ignored.append((other, f"{other.conclusion or other.status}, superseded by run {pick.id}{lent}"))
    chosen.sort(key=lambda r: (r.is_review, r.name))
    return chosen, ignored


def _fill_skipped(pick: Run, others: list[Run]) -> set[int]:
    """Give `pick` each job it skipped from the first run in `others` that ran it.

    A newer run supersedes an older one job by job, not wholesale: an edit's run
    that runs one aggregate job and skips the tests must not hide the tests that
    failed in the run before it. The price is that a job the newer run skipped on
    purpose (its label removed, say) keeps its older result until the next push.
    A cancelled job that never queued ran nothing: a stack push's cancelled
    duplicate lists the jobs its survivor skips that way.
    """
    donors = set()
    jobs: list[Job] = []
    for job in pick.jobs:
        lent = []
        if job.state == "skipped":
            for run in others:
                ran = [
                    j
                    for j in run.jobs
                    if _same_job(job.name, j.name) and j.state != "skipped" and (j.queued or j.state != "cancelled")
                ]
                if ran:
                    allowed = run.status == "completed" and run.conclusion == "success"
                    lent = [Job(j.name, j.status, j.conclusion, source=run.id, allowed=allowed) for j in ran]
                    donors.add(run.id)
                    break
        jobs.extend(lent or [job])
    pick.jobs = jobs
    return donors


def _same_job(skipped: str, ran: str) -> bool:
    """Whether a job that ran is the one a newer run skipped under `skipped`.

    A matrix job skipped by its `if` is listed once, unexpanded: `tests`, or
    `Web (${{ matrix.label }})` where the name carries an expression. Every
    expansion of it (`tests (2)`, `Web (e2e)`) is the same job.
    """
    if ran == skipped:
        return True
    base = re.sub(r"\s*\(\$\{\{.*\}\}\)\s*$", "", skipped)
    return ran.startswith(f"{base} (") and (base != skipped or "${{" not in skipped)


def judge_run(gh: GitHub, repo: str, run: Run, out: Assessment, verbose: bool) -> None:
    unfinished = [j for j in run.jobs if j.status != "completed"]
    bad = [j for j in run.jobs if j.conclusion in BAD_CONCLUSIONS]
    # Only continue-on-error lets a job fail in a run that succeeded. A job lent by
    # an older run is judged by that run.
    succeeded = not unfinished and run.status == "completed" and run.conclusion == "success"
    allowed = [j for j in bad if j.allowed or (succeeded and not j.source)]
    bad = [j for j in bad if j not in allowed]
    for job in allowed:
        out.say("", f"  {job.name} failed, which its run allows (continue-on-error)")
    counts: dict[str, int] = {}
    for job in run.jobs:
        counts[job.state] = counts.get(job.state, 0) + 1
    tally = ", ".join(f"{n} {k}" for k, n in sorted(counts.items())) or "no jobs"
    out.say("run", f"{run.name}: {run.id}  {run.event}  attempt {run.attempt}  {run.status}  ({tally})")
    for job in run.jobs:
        if verbose or job.state not in ("success", "skipped") or job.source:
            source = f"  (from run {job.source})" if job.source else ""
            out.say("", f"  {job.state:<11} {job.name}{source}")

    # A lender's reruns are history the verdict rests on too.
    for past in [run, *run.lenders]:
        whose = "" if past is run else f"run {past.id}'s "
        for earlier in range(1, past.attempt):
            attempt = gh.get(f"repos/{repo}/actions/runs/{past.id}/attempts/{earlier}", fixed=True)
            if attempt.get("conclusion") in (None, "success"):
                continue
            earlier_jobs = attempt_jobs(gh, repo, past.id, earlier, finished=True)
            names = [j.name for j in earlier_jobs if j.conclusion in BAD_CONCLUSIONS]
            out.say("", f"  {whose}attempt {earlier} was {attempt['conclusion']}: {', '.join(names) or 'no job named'}")

    if bad:
        out.failures.append(f"{run.name}: {', '.join(f'{j.name} {j.conclusion}' for j in bad)}")
    elif unfinished or run.status != "completed":
        done = len(run.jobs) - len(unfinished)
        out.pending.append(f"{run.name} still running ({done}/{len(run.jobs)} jobs done)")
    elif run.conclusion in BAD_CONCLUSIONS:
        out.failures.append(f"{run.name}: the run concluded {run.conclusion} with no failing job named")


def judge_other_checks(gh: GitHub, repo: str, sha: str, out: Assessment) -> int:
    """Checks from apps other than Actions, and commit statuses: gates too, when a repo has them.

    Returns how many there were.
    """
    checks = [
        c
        for c in gh.items(f"repos/{repo}/commits/{sha}/check-runs?per_page=100", "check_runs")
        if ((c.get("app") or {}).get("slug")) != "github-actions"
    ]
    statuses = gh.items(f"repos/{repo}/commits/{sha}/status?per_page=100", "statuses")
    for check in checks:
        state = _state(check.get("status"), check.get("conclusion"))
        app = (check.get("app") or {}).get("slug", "?")
        out.say("check", f"{check.get('name')} ({app}): {state}")
        if check.get("status") != "completed":
            out.pending.append(f"{check.get('name')} still running")
        elif state in BAD_CONCLUSIONS:
            out.failures.append(f"{check.get('name')} ({app}) {state}")
    for status in statuses:
        state = status.get("state")
        out.say("status", f"{status.get('context')}: {state}")
        if state == "pending":
            out.pending.append(f"{status.get('context')} pending")
        elif state in ("failure", "error"):
            out.failures.append(f"{status.get('context')} {state}")
    return len(checks) + len(statuses)


def _prose(body: str) -> str:
    # A quoted run link or checklist inside a code block belongs to what was quoted.
    return re.sub(r"```.*?```", "", body or "", flags=re.DOTALL)


def _by_reviewer(comment: dict) -> bool:
    # claude[bot], or the same action under a repo's own app name.
    user = comment.get("user") or {}
    return user.get("type") == "Bot" and "claude" in (user.get("login") or "").lower()


def _checklist(body: str) -> list[str] | None:
    """The unticked steps of a comment's progress checklist, or None when it has none.

    The checklist runs from the first task line through blank lines and indented
    sub-items to the first line of ordinary text. Findings further down may be
    written as task lists too, and those are advice, not steps left undone.
    """
    block: list[str] = []
    for line in _prose(body).splitlines():
        task = re.match(r"^\s*- \[[ xX]\] ", line)
        if task or (block and (not line.strip() or line[:1].isspace())):
            if task:
                block.append(line)
        elif block:
            break
    if not block:
        return None
    return [re.sub(r"^\s*- \[ \] ", "", line) for line in block if re.match(r"^\s*- \[ \] ", line)]


def judge_review(
    gh: GitHub,
    repo: str,
    pr: dict,
    runs: list[Run],
    ignored: list[Run],
    changed: list[str],
    out: Assessment,
) -> None:
    head = pr["head"]["sha"]
    default = pr["base"]["repo"]["default_branch"]
    if REVIEW_PATH in changed:
        out.say("review", "none: this PR edits the review workflow, and the action skips itself on such a PR")
        out.failures.append("the review bot did not review (this PR edits its workflow); review it by hand")
        return
    # Keyed by commit, so a watch reads each copy once rather than on every poll.
    default_sha = gh.get(f"repos/{repo}/git/ref/heads/{urllib.parse.quote(default, safe='/')}")["object"]["sha"]
    try:
        on_default = gh.get(f"repos/{repo}/contents/{REVIEW_PATH}?ref={default_sha}", fixed=True)
    except GhError as exc:
        if exc.not_found:
            out.say("review", f"no {REVIEW_PATH} on {default}, so no bot review is expected")
            return
        raise
    try:
        on_head = gh.get(f"repos/{repo}/contents/{REVIEW_PATH}?ref={head}", fixed=True)
    except GhError as exc:
        if not exc.not_found:
            raise
        on_head = None
    # The action runs only when the head's copy of its workflow is byte-identical
    # to the default branch's, so a branch cut before that file last changed (or
    # stacked on one) is skipped without a word until it is rebased. Only an open
    # PR can be rebased, and the default branch may have moved since it merged.
    stale = pr["state"] == "open" and (on_head is None or on_head["sha"] != on_default["sha"])
    rebase = f"the review bot skips this head: its {REVIEW_WORKFLOW} differs from {default}'s, so rebase"
    if stale:
        out.say("review", f"this head's {REVIEW_WORKFLOW} differs from {default}'s")

    review = next((r for r in runs if r.is_review), None)
    if review is None:
        if stale:
            out.failures.append(rebase)
            return
        skipped = any(r.is_review and r.event in PR_EVENTS and r.all_skipped for r in ignored)
        why = "its job skipped (a draft, or a filter)" if skipped else "its workflow did not trigger (a filter?)"
        out.say("review", f"no review run for this head{' that ran a job' if skipped else ''} yet")
        out.wait(
            "no-review",
            REVIEW_GRACE_S,
            "no Claude review run for this head yet",
            f"the review bot did not review this head: {why}",
        )
        return
    # A run that lent the review its job, when the newest run skipped it, is the
    # one whose comment speaks for it.
    lenders = {j.source for j in review.jobs if j.source}
    candidates = [review] + [r for r in ignored if r.id in lenders]
    # The action compared this head with the default branch's copy as it stood
    # when the run began, so a head that is stale now was skipped only if that
    # copy has not changed since.
    since = min(r.started_at for r in candidates)
    skipped_head = stale and not _landed_since(gh, repo, default, default_sha, since)

    if review.status != "completed" or any(j.status != "completed" for j in review.jobs):
        # judge_run has counted it as pending already; the review is usually the last to finish.
        out.say("review", f"run {review.id} still going")
        if skipped_head:
            out.failures.append(rebase)
        return

    # A rerun keeps the run id and posts a fresh comment (or, with a sticky
    # comment, edits the old one), so only a comment written during the latest
    # attempt speaks for it.
    marker = re.compile(rf"/actions/runs/({'|'.join(str(r.id) for r in candidates)})(?!\d)")
    mine = [
        c
        for c in gh.items(f"repos/{repo}/issues/{pr['number']}/comments?per_page=100")
        if _by_reviewer(c)
        and marker.search(_prose(c.get("body", "")))
        and max(c.get("created_at") or "", c.get("updated_at") or "") >= since
    ]
    if mine:
        comment = mine[-1]
        unticked = _checklist(comment["body"])
        inline = [
            c
            for c in gh.items(f"repos/{repo}/pulls/{pr['number']}/comments?per_page=100")
            if _by_reviewer(c) and c.get("original_commit_id") == head
        ]
        out.say(
            "review",
            f"{comment['html_url']}, with {len(inline)} inline comment(s) made on this head. Read the findings:\n"
            f"gh api repos/{repo}/issues/comments/{comment.get('id')} --jq .body",
        )
        if unticked is None:
            out.say("", "its comment carries no progress checklist, so the review may never have started")
            out.failures.append(f"the review left no checklist to show it ran; rerun it: gh run rerun {review.id}")
        elif unticked:
            out.say("", "unfinished: " + "; ".join(unticked))
            out.failures.append(
                f"the review stopped partway ({len(unticked)} step(s) unticked); rerun it: gh run rerun {review.id}"
            )
        return

    if skipped_head:
        out.say("review", f"run {review.id} {review.conclusion}, with nothing to read: the action skipped this head")
        out.failures.append(rebase)
        return
    text = base64.b64decode((on_head or on_default).get("content", "")).decode("utf-8", "replace")
    setting = re.search(r"^\s*track_progress:\s*(\S.*?)\s*$", text, re.MULTILINE)
    value = re.sub(r"\s+#.*$", "", setting.group(1)).strip("\"'") if setting else "false"
    if value.lower() in ("false", "no", "off") or "${{" in value:
        how = "sets track_progress by an expression" if "${{" in value else "does not track progress"
        out.say(
            "review",
            f"run {review.id} {review.conclusion}, and this workflow {how}, so its\n"
            "silence cannot be told from a clean pass. Nothing to read.",
        )
        return
    out.say("review", f"run {review.id} {review.conclusion}, but no bot comment from its latest attempt links to it")
    out.failures.append("the review bot did not review (no comment for this head's review run)")


def _landed_since(gh: GitHub, repo: str, default: str, default_sha: str, stamp: str) -> bool:
    """Whether a change to the review workflow reached `default` after `stamp`.

    A commit's own date says when it was written, not when it landed: a merge
    commit carries its branch's older commits. So a commit that came in through a
    PR is dated by that PR's merge.
    """
    # Git lists by commit date, and a merged branch's older commits sort below
    # newer direct edits, so the window is generous for a file that rarely changes.
    for commit in gh.get(f"repos/{repo}/commits?sha={default_sha}&path={REVIEW_PATH}&per_page=10", fixed=True):
        landed = [
            p["merged_at"]
            for p in gh.items(f"repos/{repo}/commits/{commit['sha']}/pulls", fixed=True)
            if p.get("merged_at") and (p.get("base") or {}).get("ref") == default
        ]
        if (min(landed) if landed else commit["commit"]["committer"]["date"]) >= stamp:
            return True
    return False


def local_tip(repo: str, branch: str, head: str) -> tuple[str | None, str]:
    """The local branch's commit, when the working directory is a clone of `repo`, and how it stands to `head`.

    "behind" when `head` contains it, "ahead" when it contains `head` and more,
    "rewritten" when the branch was at `head` here and has since been amended or
    rebased (its reflog holds `head`), "diverged" when neither contains the other
    and the branch has commits with no copy in `head` (work made on an older head,
    or a remote rewrite that changed them), "superseded" when every commit it has
    is in `head` in some form (a remote rebase), and "unknown" when `head` has not
    been fetched here.
    """

    def git(*args: str) -> str | None:
        try:
            done = subprocess.run(["git", *args], capture_output=True, text=True, timeout=20, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return done.stdout.strip() if done.returncode == 0 else None

    remotes = git("remote", "-v") or ""
    if not re.search(rf"[/:]{re.escape(repo)}(\.git)?\s", remotes, re.IGNORECASE):
        return None, "unknown"
    tip = git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}^{{commit}}")
    if not tip or git("cat-file", "-e", f"{head}^{{commit}}") is None:
        return tip, "unknown"
    if git("merge-base", "--is-ancestor", tip, head) is not None:
        return tip, "behind"
    if git("merge-base", "--is-ancestor", head, tip) is not None:
        return tip, "ahead"
    reflog = (git("reflog", "show", "--format=%H", f"refs/heads/{branch}") or "").split()
    if head in reflog:
        return tip, "rewritten"
    # `git cherry` marks with "+" each commit of the branch with no equivalent patch in `head`.
    cherry = git("cherry", head, tip)
    if cherry is None or any(line.startswith("+") for line in cherry.splitlines()):
        return tip, "diverged"
    return tip, "superseded"


def assess_pr(
    gh: GitHub,
    repo: str,
    number: int,
    *,
    review: bool = True,
    verbose: bool = False,
    local: Callable[[str, str, str], tuple[str | None, str]] = local_tip,
    sleep: Callable[[float], None] = time.sleep,
) -> Assessment:
    out = Assessment()
    pr = gh.get(f"repos/{repo}/pulls/{number}")
    for _ in range(3):
        if pr.get("mergeable") is not None or pr["state"] != "open":
            break
        # GitHub computes mergeability on the first read after a change.
        sleep(3)
        pr = gh.get(f"repos/{repo}/pulls/{number}")
    head, ref = pr["head"]["sha"], pr["head"]["ref"]
    out.head = head
    status = "merged" if pr.get("merged") else pr["state"] + (", draft" if pr.get("draft") else "")
    out.lines.append(f"{repo}#{number}  {ref} -> {pr['base']['ref']}  ({status})")

    notes = []
    stuck = False
    on_github = None
    head_repo = (pr["head"].get("repo") or {}).get("full_name")
    if head_repo and pr["state"] == "open":
        try:
            on_github = gh.get(f"repos/{head_repo}/git/ref/heads/{urllib.parse.quote(ref, safe='/')}")["object"]["sha"]
        except GhError as exc:
            if not exc.not_found:
                raise
            on_github = None
            notes.append("branch deleted on GitHub")
        if on_github == head:
            notes.append("matches its branch on GitHub")
        elif on_github:
            notes.append(f"but its branch on GitHub is at {on_github[:10]}")
            stuck = True
            out.wait(
                "stuck-head",
                STUCK_GRACE_S,
                f"the PR's head is still {head[:10]} though its branch is at {on_github[:10]}, so no CI runs "
                "for the new commit. If you pushed seconds ago, ask again; if it persists, amend to a new "
                "SHA and push with --force-with-lease",
                f"the PR's head has not followed its branch for {STUCK_GRACE_S // 60} min: amend to a new SHA "
                "and push with --force-with-lease",
            )
    # A fork's branch name says nothing about a local branch of the same name.
    own = (head_repo or "").lower() == repo.lower()
    mine, standing = local(repo, ref, head) if own else (None, "unknown")
    if mine == head:
        notes.append("matches the local branch")
    elif mine and standing in ("ahead", "rewritten") and mine != on_github:
        notes.append(
            f"local {ref} is at {mine[:10]}, {'rewritten' if standing == 'rewritten' else 'ahead'} and unpushed"
        )
        out.failures.append(f"local {ref} has work the PR's head does not, so none of this describes it: push")
    elif mine and standing == "diverged" and mine != on_github:
        notes.append(f"local {ref} is at {mine[:10]}, diverged from it with commits it has no copy of")
        out.failures.append(
            f"local {ref} and the PR's head have diverged, so this may not describe the local work: "
            "reconcile them (fetch, then rebase or reset) before trusting it"
        )
    elif mine:
        how = {"behind": "behind it", "ahead": "pushed", "superseded": "superseded by it"}.get(standing, "not compared")
        notes.append(f"local {ref} is at {mine[:10]} ({how})")
    out.say("head", f"{head[:10]}" + (f"  ({'; '.join(notes)})" if notes else ""))
    if stuck:
        out.say("CI", "not read: it would describe a head the branch has moved past")
        return out

    if pr["state"] == "open":
        if pr.get("mergeable") is False or pr.get("mergeable_state") == "dirty":
            out.say("mergeable", "no: CONFLICTING")
            out.failures.append(
                "the PR conflicts with its base, so GitHub has no merge ref and pull_request CI will not "
                "run until it is rebased. Any 'no checks' reading means nothing was validated"
            )
        elif pr.get("mergeable") is None:
            out.say("mergeable", "not yet computed by GitHub")
            out.pending.append("GitHub has not computed mergeability yet")
        else:
            out.say("mergeable", f"yes ({pr.get('mergeable_state')})")

    runs = fetch_runs(gh, repo, head, pr=number, branch=ref, review=review)
    other_checks = judge_other_checks(gh, repo, head, out)
    chosen, ignored = _judge_runs(gh, repo, runs, out, verbose, other_checks=other_checks)
    if review:
        files = gh.items(
            f"repos/{repo}/pulls/{number}/files?per_page=100", fixed=True, version=f"{head}..{pr['base']['sha']}"
        )
        changed = [f["filename"] for f in files] + [f["previous_filename"] for f in files if f.get("previous_filename")]
        judge_review(gh, repo, pr, chosen, ignored, changed, out)
    return out


def assess_commit(gh: GitHub, repo: str, sha: str, *, verbose: bool = False) -> Assessment:
    full = gh.get(f"repos/{repo}/commits/{sha}", fixed=True)["sha"]
    out = Assessment(head=full)
    out.lines.append(f"{repo}@{full[:10]}")
    other_checks = judge_other_checks(gh, repo, full, out)
    _judge_runs(gh, repo, fetch_runs(gh, repo, full), out, verbose, other_checks=other_checks)
    return out


def _judge_runs(
    gh: GitHub, repo: str, runs: list[Run], out: Assessment, verbose: bool, *, other_checks: int
) -> tuple[list[Run], list[Run]]:
    chosen, ignored = choose_runs(runs)
    # The review reads the change; it tests nothing, so it cannot stand in for CI.
    # Another app's check or a commit status can.
    tested = any(not r.is_review for r in chosen) or (other_checks > 0 and not _actions_ci(gh, repo))
    skipped = [r for r, _ in ignored if r.event in GATE_EVENTS and r.all_skipped and not r.is_review]
    if not tested and skipped:
        out.say("CI", "every run for this commit so far skipped all its jobs")
        out.wait(
            "all-skipped",
            ALL_SKIPPED_GRACE_S,
            "every run so far skipped all its jobs (a draft, or a filter); runs a new event starts may follow",
            "nothing was tested: every run for this commit skipped all its jobs (a draft, or a filter)",
        )
    elif not tested:
        out.say("CI", "no gating run registered for this commit")
        out.wait(
            "no-runs",
            NO_RUNS_GRACE_S,
            "no runs yet: GitHub registers them a few seconds after a push, so ask again (or --watch)",
            "no workflow ran for this commit ([skip ci], a paths filter, or no trigger for its event)",
        )
    for run in chosen:
        judge_run(gh, repo, run, out, verbose)
    others: dict[str, int] = {}
    for run, why in ignored:
        if run.event in GATE_EVENTS:
            out.say("ignored", f"{run.name}: {run.id}, {why}")
        else:
            others[run.event] = others.get(run.event, 0) + 1
    for event, n in sorted(others.items()):
        out.say("ignored", f"{n} {event} run(s), which are not gates")
    return chosen, [run for run, _ in ignored]


def _actions_ci(gh: GitHub, repo: str) -> bool:
    """Whether the repo has an active workflow besides the review, so Actions runs are to be waited for."""
    workflows = gh.items(f"repos/{repo}/actions/workflows?per_page=100", "workflows", fixed=True)
    return any(
        w.get("state") == "active" and w.get("path", "").startswith(".github/workflows/") and w["path"] != REVIEW_PATH
        for w in workflows
    )


def escalate(result: Assessment, seen: dict[str, float], now: float) -> None:
    """Turn each wait that has lasted its grace, as far as this watch has seen, into a failure."""
    for key in list(seen):
        if key not in result.waits:
            del seen[key]
    for key, (grace, failure) in result.waits.items():
        if now - seen.setdefault(key, now) >= grace:
            result.failures.append(failure)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("pr", nargs="?", type=int, help="pull request number (default: the current branch's)")
    parser.add_argument("-R", "--repo", help="owner/name (default: the current directory's repository)")
    parser.add_argument("--commit", help="judge the runs for a commit instead of a PR, e.g. a merge to main")
    parser.add_argument("--watch", action="store_true", help="poll until the state settles")
    parser.add_argument("--interval", type=float, default=30, help="seconds between polls (default 30)")
    parser.add_argument("--timeout", type=float, default=60, help="minutes --watch waits (default 60)")
    parser.add_argument("--no-review", action="store_true", help="do not require a Claude review")
    parser.add_argument("-v", "--verbose", action="store_true", help="list every job, not only those not passing")
    args = parser.parse_args(argv)
    if args.pr and args.commit:
        parser.error("give a PR or --commit, not both")
    if args.repo and not (args.pr or args.commit):
        parser.error("with -R, name the PR (or --commit); the current branch belongs to this directory's repo")

    def say_unreadable(exc: Exception) -> int:
        print(f"could not read GitHub, so there is no verdict: {exc}", file=sys.stderr)
        return EXIT_UNREADABLE

    try:
        repo = args.repo or _gh(["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]).strip()
        number = args.pr
        if not number and not args.commit:
            number = int(_gh(["pr", "view", "--json", "number", "--jq", ".number"]).strip())
    except GhError as exc:
        if exc.transient:
            return say_unreadable(exc)
        parser.error(f"name the PR and -R owner/repo; they could not be worked out here ({exc})")

    gh = GitHub()

    def assess() -> Assessment:
        if args.commit:
            return assess_commit(gh, repo, args.commit, verbose=args.verbose)
        return assess_pr(gh, repo, number, review=not args.no_review, verbose=args.verbose)

    def refused(exc: GhError) -> int:
        print(f"GitHub refused the question, so check the PR, -R and --commit: {exc}", file=sys.stderr)
        return 2

    deadline = time.time() + args.timeout * 60
    seen: dict[str, float] = {}
    errors = 0
    while True:
        try:
            result = assess()
            errors = 0
        except GhError as exc:
            if not exc.transient:
                return refused(exc)
            failed: Exception = exc
        except Exception as exc:  # noqa: BLE001 - any crash here must not read as a red build
            failed = exc
        else:
            if args.watch:
                escalate(result, seen, time.time())
            if not args.watch or result.state != PENDING or time.time() >= deadline:
                break
            print(f"{time.strftime('%H:%M:%S')}  {result.verdict()}", file=sys.stderr, flush=True)
            time.sleep(args.interval)
            continue
        # A 502 or a rate limit says nothing about CI, so a watch asks again.
        errors += 1
        if not args.watch or errors >= WATCH_ERRORS or time.time() >= deadline:
            return say_unreadable(failed)
        print(f"{time.strftime('%H:%M:%S')}  could not read GitHub, trying again: {failed}", file=sys.stderr)
        time.sleep(args.interval)
    print("\n".join(result.lines))
    print(result.verdict())
    return EXIT[result.state]


if __name__ == "__main__":
    sys.exit(main())
