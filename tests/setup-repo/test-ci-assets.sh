#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
CI="$ROOT/plugins/core/skills/setup-repo/assets/ci/ci-python.yml"
EC="$ROOT/plugins/core/skills/setup-repo/assets/editorconfig"

python3 - "$CI" <<'EOF'
import sys
try:
    import yaml
except ModuleNotFoundError:
    print("pyyaml missing; skipping YAML parse"); sys.exit(0)
doc = yaml.safe_load(open(sys.argv[1]))
# GitHub Actions `on:` is parsed as the boolean True by PyYAML (YAML 1.1), so accept either key
on = doc.get("on", doc.get(True))
assert on is not None, doc
assert on["push"]["branches"] == ["main"], on
assert "pull_request" in on, on
steps = doc["jobs"]["lint-and-test"]["steps"]
runs = "\n".join(s.get("run", "") for s in steps)
assert "ruff check ." in runs, runs
assert "ruff format --check ." in runs, runs
assert "pytest" in runs, runs
assert "requirements.txt" in runs and "requirements-dev.txt" in runs, runs
setup_py = [s for s in steps if str(s.get("uses", "")).startswith("actions/setup-python")]
assert setup_py and setup_py[0]["with"]["python-version"] == "3.12", setup_py
print("ci-python.yml OK")
EOF

grep -q "root = true" "$EC"
grep -q "indent_size = 4" "$EC"   # python
grep -q "indent_size = 2" "$EC"   # js/ts/yaml
echo "ci assets OK"
