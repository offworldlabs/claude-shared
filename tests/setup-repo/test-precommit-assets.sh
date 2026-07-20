#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
PC="$ROOT/plugins/core/skills/setup-repo/assets/precommit"

python3 - "$PC/python.yaml" "$PC/ts.yaml" <<'EOF'
import sys
try:
    import yaml
except ModuleNotFoundError:
    print("pyyaml missing; skipping precommit YAML parse"); sys.exit(0)
py = yaml.safe_load(open(sys.argv[1]))
ts = yaml.safe_load(open(sys.argv[2]))

def by_repo(doc):
    return {r.get("repo"): r for r in doc["repos"]}

HYGIENE = "https://github.com/pre-commit/pre-commit-hooks"
RUFF = "https://github.com/astral-sh/ruff-pre-commit"
need_hygiene = {"trailing-whitespace", "end-of-file-fixer", "check-yaml",
                "check-json", "check-merge-conflict", "check-added-large-files"}

pr = by_repo(py)
assert HYGIENE in pr, pr.keys()
assert RUFF in pr, pr.keys()
assert need_hygiene <= {h["id"] for h in pr[HYGIENE]["hooks"]}, pr[HYGIENE]
assert {"ruff", "ruff-format"} <= {h["id"] for h in pr[RUFF]["hooks"]}, pr[RUFF]
print("python.yaml OK")

tr = by_repo(ts)
assert HYGIENE in tr, tr.keys()
assert need_hygiene <= {h["id"] for h in tr[HYGIENE]["hooks"]}, tr[HYGIENE]
assert "local" in tr, tr.keys()
local_hooks = tr["local"]["hooks"]
assert any(h.get("id") == "eslint" and "eslint" in h.get("entry", "") for h in local_hooks), local_hooks
print("ts.yaml OK")
EOF
echo "precommit assets OK"
