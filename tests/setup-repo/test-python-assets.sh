#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
PY="$ROOT/plugins/core/skills/setup-repo/assets/stack/python"

python3 - "$PY/pyproject.toml" <<'EOF'
import sys, tomllib
data = tomllib.load(open(sys.argv[1], "rb"))
ruff = data["tool"]["ruff"]
assert ruff["target-version"] == "py312", ruff
assert ruff["line-length"] == 120, ruff
assert data["tool"]["ruff"]["lint"]["select"] == ["E", "F", "W"], ruff
assert data["tool"]["ruff"]["format"]["quote-style"] == "double", ruff
assert data["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"], data
print("pyproject.toml OK")
EOF

grep -qE 'ruff>=0\.8' "$PY/requirements-dev.txt"
grep -qE 'pytest>=8' "$PY/requirements-dev.txt"
test -f "$PY/gitignore" && grep -q "__pycache__" "$PY/gitignore"
test -f "$PY/tests/.gitkeep"
echo "python assets OK"
