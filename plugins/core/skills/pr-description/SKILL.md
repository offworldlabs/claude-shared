---
name: pr-description
description: Use when opening a pull request or when the user asks to write, draft, or generate a PR description, PR summary, or PR body. Reads the branch diff and produces a review-ready description.
---

# PR Description

Write a clear, review-ready pull request description from the current branch's changes.

## Steps

1. Determine the base branch (usually `main`) and gather the diff:
   - `git merge-base HEAD main` to find the fork point.
   - `git diff <base>...HEAD --stat` for the file-level overview.
   - `git diff <base>...HEAD` for the full change, and `git log <base>..HEAD` for commit context.
2. Read the changes closely enough to explain *what* changed and *why*, not just which files moved.
3. Produce the description with these sections:
   - **Summary** — 1-3 sentences on what this PR does and the motivation behind it.
   - **Changes** — bulleted list of the notable changes, grouped by area or concern.
   - **Test coverage** — what tests were added or updated, what was run to verify, and any gaps.
   - **Review notes** — anything reviewers should scrutinise: risky areas, trade-offs, follow-ups, migrations, or intentionally deferred work.
4. Keep it concise and factual. Do not invent testing that wasn't done — if coverage is thin, say so under Review notes.

Output the description as Markdown ready to paste into the PR body.
