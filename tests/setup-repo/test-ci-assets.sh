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
jobs = doc["jobs"]["lint-and-test"]["steps"]
names = [s.get("name", "") for s in jobs]
assert any("Ruff" in n for n in names), names
assert any("Pytest" in n or "pytest" in n for n in names), names
print("ci-python.yml OK")
EOF

grep -q "root = true" "$EC"
grep -q "indent_size = 4" "$EC"   # python
grep -q "indent_size = 2" "$EC"   # js/ts/yaml
echo "ci assets OK"
