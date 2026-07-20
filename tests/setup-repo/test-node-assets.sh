#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
STK="$ROOT/plugins/core/skills/setup-repo/assets/stack"

check_pkg() { # check_pkg <dir> <needs-react:0|1>
  local dir="$1" needs_react="$2"
  python3 - "$dir/package.json" "$needs_react" <<'EOF'
import json, sys
pkg = json.load(open(sys.argv[1]))
needs_react = sys.argv[2] == "1"
scripts = pkg.get("scripts", {})
for s in ("typecheck", "lint", "test"):
    assert s in scripts, f"missing script {s}: {scripts}"
assert scripts["lint"] == "eslint .", scripts
assert scripts["typecheck"] == "tsc --noEmit", scripts
assert scripts["test"] == "vitest run", scripts
dev = pkg.get("devDependencies", {})
for d in ("eslint", "typescript", "typescript-eslint", "vitest", "@eslint/js"):
    assert d in dev, f"missing devDep {d}: {dev}"
if needs_react:
    deps = pkg.get("dependencies", {})
    assert "react" in deps and "react-dom" in deps, deps
    assert "vite" in dev and "@vitejs/plugin-react" in dev, dev
print(f"{sys.argv[1]} OK")
EOF
}

check_stack_files() { # check_stack_files <dir>
  local dir="$1"
  for f in package.json tsconfig.json eslint.config.js vitest.config.ts gitignore \
           src/index.ts src/index.test.ts; do
    test -f "$dir/$f" || { echo "MISSING: $dir/$f" >&2; exit 1; }
  done
  python3 -c "import json; json.load(open('$dir/tsconfig.json'))"
  grep -q 'node_modules' "$dir/gitignore"
  grep -q 'typescript-eslint' "$dir/eslint.config.js"
}

check_stack_files "$STK/ts-frontend"
check_pkg "$STK/ts-frontend" 1
echo "ts-frontend assets OK"

check_stack_files "$STK/ts-backend"
check_pkg "$STK/ts-backend" 0
echo "ts-backend assets OK"

CI="$ROOT/plugins/core/skills/setup-repo/assets/ci/ci-node.yml"
python3 - "$CI" <<'EOF'
import sys
try:
    import yaml
except ModuleNotFoundError:
    print("pyyaml missing; skipping ci-node YAML parse"); sys.exit(0)
doc = yaml.safe_load(open(sys.argv[1]))
on = doc.get("on", doc.get(True))
assert on["push"]["branches"] == ["main"], on
assert "pull_request" in on, on
steps = doc["jobs"]["lint-and-test"]["steps"]
uses = [str(s.get("uses", "")) for s in steps]
assert any(u.startswith("actions/setup-node") for u in uses), uses
runs = "\n".join(s.get("run", "") for s in steps)
assert "npm ci" in runs, runs
assert "npm run typecheck" in runs, runs
assert "npm run lint" in runs, runs
assert "npm test" in runs, runs
print("ci-node.yml OK")
EOF
echo "node ci asset OK"
