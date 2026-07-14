#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
ENGINE="$ROOT/plugins/core/skills/setup-repo/scripts/scaffold-repo.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git -C "$TMP" init -q

bash "$ENGINE" "$TMP" python

for f in .claude/settings.json CLAUDE.md .claude/rules/security.md \
         .claude/rules/code-style.md .github/workflows/claude.yml \
         .github/workflows/claude-code-review.yml .github/workflows/ci.yml \
         .editorconfig pyproject.toml requirements.txt requirements-dev.txt \
         .gitignore tests/.gitkeep; do
  test -e "$TMP/$f" || { echo "MISSING: $f" >&2; exit 1; }
done

python3 -c "import json; json.load(open('$TMP/.claude/settings.json'))"
python3 -c "import tomllib; tomllib.load(open('$TMP/pyproject.toml','rb'))"

# non-clobber: second run skips everything and reports it
out="$(bash "$ENGINE" "$TMP" python)"
echo "$out" | grep -q "SKIPPED" || { echo "expected SKIPPED report" >&2; exit 1; }
echo "$out" | grep -q "pyproject.toml" || { echo "expected skipped file listed" >&2; exit 1; }

# scaffolded python defaults are internally consistent
mkdir -p "$TMP/src"
cat > "$TMP/src/example.py" <<'PY'
def add(a: int, b: int) -> int:
    return a + b
PY
cat > "$TMP/tests/test_example.py" <<'PY'
from src.example import add


def test_add() -> None:
    assert add(2, 3) == 5
PY
if command -v ruff >/dev/null 2>&1; then
  ( cd "$TMP" && ruff format . >/dev/null && ruff check . && ruff format --check . )
  echo "ruff OK"
else
  echo "ruff not installed; skipped"
fi
if command -v pytest >/dev/null 2>&1; then
  ( cd "$TMP" && PYTHONPATH=. pytest -q )
  echo "pytest OK"
else
  echo "pytest not installed; skipped"
fi

# unknown stack exits 2
if bash "$ENGINE" "$TMP" bogus 2>/dev/null; then
  echo "expected non-zero exit for unknown stack" >&2; exit 1
fi
echo "ALL CHECKS PASSED"
