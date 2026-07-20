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

# non-clobber: second run skips everything and reports it, leaving files byte-identical
before="$(shasum "$TMP/pyproject.toml")"
out="$(bash "$ENGINE" "$TMP" python)"
echo "$out" | grep -q "SKIPPED" || { echo "expected SKIPPED report" >&2; exit 1; }
echo "$out" | grep -q "pyproject.toml" || { echo "expected skipped file listed" >&2; exit 1; }
after="$(shasum "$TMP/pyproject.toml")"
[ "$before" = "$after" ] || { echo "skipped file was modified" >&2; exit 1; }

# none stack: writes the always-files, omits all python-only files
TMP_NONE="$(mktemp -d)"
trap 'rm -rf "$TMP" "$TMP_NONE"' EXIT
git -C "$TMP_NONE" init -q
bash "$ENGINE" "$TMP_NONE" none
for f in .claude/settings.json CLAUDE.md .claude/rules/security.md \
         .claude/rules/code-style.md .github/workflows/claude.yml \
         .github/workflows/claude-code-review.yml .editorconfig; do
  test -e "$TMP_NONE/$f" || { echo "MISSING (none stack): $f" >&2; exit 1; }
done
for f in pyproject.toml requirements.txt requirements-dev.txt .gitignore \
         tests/.gitkeep .github/workflows/ci.yml; do
  test -e "$TMP_NONE/$f" && { echo "UNEXPECTED (none stack): $f" >&2; exit 1; }
done

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

# unknown stack exits 2 and writes nothing
BOGUS="$(mktemp -d)"
trap 'rm -rf "$TMP" "$TMP_NONE" "$BOGUS"' EXIT
git -C "$BOGUS" init -q
set +e; bash "$ENGINE" "$BOGUS" bogus >/dev/null 2>&1; rc=$?; set -e
[ "$rc" -eq 2 ] || { echo "expected exit 2 for unknown stack, got $rc" >&2; exit 1; }
[ -z "$(ls -A "$BOGUS" | grep -v '^.git$' || true)" ] || { echo "unknown stack wrote files" >&2; exit 1; }

# ts-frontend: writes node/ts files + ci.yml, omits python-only files
TMP_TSF="$(mktemp -d)"
trap 'rm -rf "$TMP" "$TMP_NONE" "$BOGUS" "$TMP_TSF"' EXIT
git -C "$TMP_TSF" init -q
bash "$ENGINE" "$TMP_TSF" ts-frontend
for f in .claude/settings.json CLAUDE.md .editorconfig \
         package.json tsconfig.json eslint.config.js vitest.config.ts .gitignore \
         src/index.ts src/index.test.ts .github/workflows/ci.yml \
         .github/workflows/claude.yml; do
  test -e "$TMP_TSF/$f" || { echo "MISSING (ts-frontend): $f" >&2; exit 1; }
done
for f in pyproject.toml requirements.txt requirements-dev.txt; do
  test -e "$TMP_TSF/$f" && { echo "UNEXPECTED (ts-frontend): $f" >&2; exit 1; }
done
python3 -c "import json; json.load(open('$TMP_TSF/package.json'))"
grep -q '"react"' "$TMP_TSF/package.json" || { echo "ts-frontend missing react" >&2; exit 1; }
grep -q 'npm ci' "$TMP_TSF/.github/workflows/ci.yml" || { echo "ts-frontend ci not node" >&2; exit 1; }

# ts-backend: same file set, no react
TMP_TSB="$(mktemp -d)"
trap 'rm -rf "$TMP" "$TMP_NONE" "$BOGUS" "$TMP_TSF" "$TMP_TSB"' EXIT
git -C "$TMP_TSB" init -q
bash "$ENGINE" "$TMP_TSB" ts-backend
for f in package.json tsconfig.json eslint.config.js vitest.config.ts .gitignore \
         src/index.ts .github/workflows/ci.yml; do
  test -e "$TMP_TSB/$f" || { echo "MISSING (ts-backend): $f" >&2; exit 1; }
done
grep -q '"react"' "$TMP_TSB/package.json" && { echo "ts-backend should not have react" >&2; exit 1; }
echo "ALL CHECKS PASSED"
