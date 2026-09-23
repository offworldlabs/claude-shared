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

APP="$ROOT/plugins/core/skills/setup-repo/assets/stack/python-app"
python3 - "$APP/pyproject.toml" "$PY/pyproject.toml" <<'EOF'
import sys, tomllib
app = tomllib.load(open(sys.argv[1], "rb"))
lib = tomllib.load(open(sys.argv[2], "rb"))
project = app["project"]
assert project["requires-python"] == "==3.12.*", project
assert project["dependencies"] == [], project
dev = " ".join(app["dependency-groups"]["dev"])
for tool in ("ruff", "pytest", "pre-commit"):
    assert tool in dev, (tool, dev)
assert app["tool"]["uv"]["package"] is False, app["tool"]["uv"]
# lint config matches the library scaffold, so the two stacks format alike
assert app["tool"]["ruff"] == lib["tool"]["ruff"], (app["tool"]["ruff"], lib["tool"]["ruff"])
assert app["tool"]["pytest"]["ini_options"]["pythonpath"] == ["."], app["tool"]["pytest"]
print("python-app pyproject.toml OK")
EOF
# an app has no requirements files: the lock is the only record
if ls "$APP" | grep -q '^requirements'; then
  echo "python-app ships a requirements file" >&2; exit 1
fi
echo "python-app assets OK"
