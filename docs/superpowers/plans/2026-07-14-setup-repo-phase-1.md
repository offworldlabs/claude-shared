# `core:setup-repo` Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a `core:setup-repo` skill that scaffolds a new org repo to standard (Claude enablement + Claude workflows + Python stack), driven by Claude Code, with all files bundled as plugin assets.

**Architecture:** The plugin is the single source of truth. Static template files live under `plugins/core/skills/setup-repo/assets/`. A deterministic bash engine (`scaffold-repo.sh`) copies them into a target repo without clobbering existing files; the `SKILL.md` procedure orchestrates the engine plus the interactive parts (stack choice, first install, fleshing out `CLAUDE.md`). PR #1's root `templates/` and `rules/` are folded into the plugin.

**Tech Stack:** Claude Code plugin (marketplace `offworld`), bash (engine + test harness), Python tooling defaults (ruff, pytest) as scaffolded assets.

## Global Constraints

- Marketplace name: `offworld`; plugin: `core`; skill namespace: `core:setup-repo`.
- Only `plugin.json`/`marketplace.json` live in `.claude-plugin/`; components at plugin root.
- Delivery model: self-contained plugin; skill references assets via `${CLAUDE_PLUGIN_ROOT}`. No runtime fetch.
- Python defaults (verbatim): ruff `target-version = "py312"`, `line-length = 120`, `[tool.ruff.lint] select = ["E", "F", "W"]`, `[tool.ruff.format] quote-style = "double"`; pytest `testpaths = ["tests"]`; pip + `requirements.txt` / `requirements-dev.txt`.
- Dotfile assets are stored WITHOUT the leading dot (`gitignore`, `editorconfig`) so they aren't hidden/ignored in the marketplace repo; the engine renames them on copy.
- Idempotent, never silently clobber: existing files are skipped and reported, never overwritten.
- CI workflows carry the write-permission fix (`pull-requests: write`, `issues: write`); they only take effect once on the target repo's default branch.
- Working branch for execution: `feat/offworld-marketplace-scaffold` (continues PR #1 into the Phase 1 deliverable). Phase 2 (ts-frontend/ts-backend) and Phase 3 (pre-commit, C++) are out of scope here.

---

### Task 1: Restructure — fold PR #1 templates into plugin assets

**Files:**
- Move: `templates/settings.json` → `plugins/core/skills/setup-repo/assets/claude/settings.json`
- Move: `templates/CLAUDE.md` → `plugins/core/skills/setup-repo/assets/claude/CLAUDE.md`
- Move: `templates/github-workflows/claude-code-review.yml` → `plugins/core/skills/setup-repo/assets/ci/claude-code-review.yml`
- Move: `templates/github-workflows/claude.yml` → `plugins/core/skills/setup-repo/assets/ci/claude.yml`
- Move: `rules/security.md` → `plugins/core/skills/setup-repo/assets/rules/security.md`
- Move: `rules/code-style.md` → `plugins/core/skills/setup-repo/assets/rules/code-style.md`
- Delete: root `templates/`, root `rules/`
- Modify: `README.md` (adoption section)

**Interfaces:**
- Produces: the `assets/claude/`, `assets/ci/`, `assets/rules/` directories that Task 4's engine copies from.

- [ ] **Step 1: Move the files with git mv**

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p plugins/core/skills/setup-repo/assets/{claude,ci,rules}
git mv templates/settings.json                       plugins/core/skills/setup-repo/assets/claude/settings.json
git mv templates/CLAUDE.md                           plugins/core/skills/setup-repo/assets/claude/CLAUDE.md
git mv templates/github-workflows/claude-code-review.yml plugins/core/skills/setup-repo/assets/ci/claude-code-review.yml
git mv templates/github-workflows/claude.yml         plugins/core/skills/setup-repo/assets/ci/claude.yml
git mv rules/security.md                             plugins/core/skills/setup-repo/assets/rules/security.md
git mv rules/code-style.md                           plugins/core/skills/setup-repo/assets/rules/code-style.md
rmdir templates/github-workflows templates rules 2>/dev/null || true
```

- [ ] **Step 2: Update the rules-file symlink comment**

The two rules files still contain a comment saying they get "symlinked into each repo's `.claude/rules/`". The model is now copy, not symlink. In BOTH `plugins/core/skills/setup-repo/assets/rules/security.md` and `.../code-style.md`, replace the comment block's line:

```
  These files are symlinked into each consuming repo's .claude/rules/ so every
```

with:

```
  The setup-repo skill copies these into each consuming repo's .claude/rules/ so every
```

- [ ] **Step 3: Rewrite the README adoption section**

In `README.md`, replace the entire "## Adopting in a consuming repo" section (down to, but not including, "## Contributing") with:

```markdown
## Adopting in a consuming repo

Adoption is driven by Claude Code, not manual copying. Once, per machine, install
the plugin at user scope:

```
/plugin marketplace add offworldlabs/claude-shared
/plugin install core@offworld
```

Then, in any new repo, start Claude Code and ask:

> set this repo up per `claude-shared`

Claude invokes the `core:setup-repo` skill, which writes `.claude/settings.json`
(registering the marketplace and enabling `core`), a `CLAUDE.md`, the shared rules,
the Claude review workflows, and your stack's tooling — then installs deps and
helps you flesh out `CLAUDE.md`. See `docs/runbooks/github-actions-claude-review.md`
for the one manual follow-up (the `CLAUDE_CODE_OAUTH_TOKEN` secret).
```

- [ ] **Step 4: Validate the plugin still loads**

Run: `claude plugin validate .`
Expected: `Validation passed` (no error). The moved workflow/settings files are now plugin assets, not components, so they don't affect validation.

- [ ] **Step 5: Verify old paths are gone and new ones exist**

Run:
```bash
test ! -d templates && test ! -d rules && echo "root dirs removed"
ls plugins/core/skills/setup-repo/assets/claude/settings.json \
   plugins/core/skills/setup-repo/assets/ci/claude.yml \
   plugins/core/skills/setup-repo/assets/rules/security.md
```
Expected: prints "root dirs removed" and lists the three files with no error.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "Fold root templates and rules into setup-repo plugin assets"
```

---

### Task 2: Python stack assets

**Files:**
- Create: `plugins/core/skills/setup-repo/assets/stack/python/pyproject.toml`
- Create: `plugins/core/skills/setup-repo/assets/stack/python/requirements.txt`
- Create: `plugins/core/skills/setup-repo/assets/stack/python/requirements-dev.txt`
- Create: `plugins/core/skills/setup-repo/assets/stack/python/gitignore`
- Create: `plugins/core/skills/setup-repo/assets/stack/python/tests/.gitkeep`

**Interfaces:**
- Produces: the `assets/stack/python/` tree Task 4's engine copies when `stack == python`.

- [ ] **Step 1: Write a failing validation check**

Create `tests/setup-repo/test-python-assets.sh`:

```bash
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

grep -q "ruff" "$PY/requirements-dev.txt"
grep -q "pytest" "$PY/requirements-dev.txt"
test -f "$PY/gitignore" && grep -q "__pycache__" "$PY/gitignore"
test -f "$PY/tests/.gitkeep"
echo "python assets OK"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash tests/setup-repo/test-python-assets.sh`
Expected: FAIL (the `assets/stack/python/*` files don't exist yet — `tomllib.load` raises `FileNotFoundError`).

- [ ] **Step 3: Create the Python assets**

`plugins/core/skills/setup-repo/assets/stack/python/pyproject.toml`:
```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W"]

[tool.ruff.format]
quote-style = "double"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`plugins/core/skills/setup-repo/assets/stack/python/requirements.txt`:
```
# Runtime dependencies for this project. Add them below, pinned where practical.
```

`plugins/core/skills/setup-repo/assets/stack/python/requirements-dev.txt`:
```
ruff>=0.8.0
pytest>=8.0.0
```

`plugins/core/skills/setup-repo/assets/stack/python/gitignore`:
```
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.venv/
venv/
*.egg-info/
build/
dist/
.env
```

`plugins/core/skills/setup-repo/assets/stack/python/tests/.gitkeep`: (empty file)

- [ ] **Step 4: Run the check to verify it passes**

Run: `bash tests/setup-repo/test-python-assets.sh`
Expected: prints `pyproject.toml OK` then `python assets OK`.

- [ ] **Step 5: Commit**

```bash
git add plugins/core/skills/setup-repo/assets/stack/python tests/setup-repo/test-python-assets.sh
git commit -m "Add Python stack assets (ruff py312, pytest) with validation"
```

---

### Task 3: CI and editorconfig assets

**Files:**
- Create: `plugins/core/skills/setup-repo/assets/ci/ci-python.yml`
- Create: `plugins/core/skills/setup-repo/assets/editorconfig`

**Interfaces:**
- Produces: `assets/ci/ci-python.yml` (copied to `.github/workflows/ci.yml` for python) and `assets/editorconfig` (copied to `.editorconfig`), both used by Task 4's engine.

- [ ] **Step 1: Write a failing validation check**

Create `tests/setup-repo/test-ci-assets.sh`:

```bash
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash tests/setup-repo/test-ci-assets.sh`
Expected: FAIL (files don't exist; `open(sys.argv[1])` raises `FileNotFoundError`).

- [ ] **Step 3: Create the CI and editorconfig assets**

`plugins/core/skills/setup-repo/assets/ci/ci-python.yml`:
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Ruff lint
        run: ruff check .

      - name: Ruff format check
        run: ruff format --check .

      - name: Pytest
        run: pytest
```

`plugins/core/skills/setup-repo/assets/editorconfig`:
```
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space

[*.py]
indent_size = 4

[*.{js,jsx,ts,tsx,json,yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

- [ ] **Step 4: Run the check to verify it passes**

Run: `bash tests/setup-repo/test-ci-assets.sh`
Expected: prints `ci-python.yml OK` (or the pyyaml-missing skip line) then `ci assets OK`.

- [ ] **Step 5: Commit**

```bash
git add plugins/core/skills/setup-repo/assets/ci/ci-python.yml plugins/core/skills/setup-repo/assets/editorconfig tests/setup-repo/test-ci-assets.sh
git commit -m "Add Python CI workflow and shared editorconfig assets"
```

---

### Task 4: Deterministic scaffold engine + end-to-end test

**Files:**
- Create: `plugins/core/skills/setup-repo/scripts/scaffold-repo.sh`
- Create: `tests/setup-repo/test-scaffold.sh`

**Interfaces:**
- Consumes: all `assets/**` from Tasks 1-3.
- Produces: `scaffold-repo.sh <target_dir> <stack>` where `<stack>` is `python` or `none`; copies assets into `<target_dir>`, renaming `gitignore`→`.gitignore` and `editorconfig`→`.editorconfig`, skipping (not overwriting) existing files, and printing `WRITTEN:` / `SKIPPED:` reports. Exit code 2 on unknown stack. Task 5's SKILL.md calls this.

- [ ] **Step 1: Write the failing end-to-end test**

Create `tests/setup-repo/test-scaffold.sh`:

```bash
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash tests/setup-repo/test-scaffold.sh`
Expected: FAIL (`scaffold-repo.sh` does not exist — `bash "$ENGINE"` errors "No such file or directory").

- [ ] **Step 3: Write the engine**

`plugins/core/skills/setup-repo/scripts/scaffold-repo.sh`:
```bash
#!/usr/bin/env bash
# Deterministic file-scaffolding engine for the core:setup-repo skill.
# Copies bundled assets into a target repo without clobbering existing files.
# Usage: scaffold-repo.sh <target_dir> <stack>
#   <stack>: python | none   (ts-frontend / ts-backend land in Phase 2)
set -euo pipefail

TARGET="${1:?target dir required}"
STACK="${2:-none}"
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../assets" && pwd)"

written=()
skipped=()

copy() { # copy <src> <dest>
  local src="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if [[ -e "$dest" ]]; then
    skipped+=("$dest")
  else
    cp "$src" "$dest"
    written+=("$dest")
  fi
}

# Claude enablement (always)
copy "$ASSETS/claude/settings.json"      "$TARGET/.claude/settings.json"
copy "$ASSETS/claude/CLAUDE.md"          "$TARGET/CLAUDE.md"
copy "$ASSETS/rules/security.md"         "$TARGET/.claude/rules/security.md"
copy "$ASSETS/rules/code-style.md"       "$TARGET/.claude/rules/code-style.md"

# Claude review workflows (always)
copy "$ASSETS/ci/claude-code-review.yml" "$TARGET/.github/workflows/claude-code-review.yml"
copy "$ASSETS/ci/claude.yml"             "$TARGET/.github/workflows/claude.yml"

# Shared
copy "$ASSETS/editorconfig"              "$TARGET/.editorconfig"

# Stack
case "$STACK" in
  python)
    copy "$ASSETS/stack/python/pyproject.toml"       "$TARGET/pyproject.toml"
    copy "$ASSETS/stack/python/requirements.txt"     "$TARGET/requirements.txt"
    copy "$ASSETS/stack/python/requirements-dev.txt" "$TARGET/requirements-dev.txt"
    copy "$ASSETS/stack/python/gitignore"            "$TARGET/.gitignore"
    copy "$ASSETS/stack/python/tests/.gitkeep"       "$TARGET/tests/.gitkeep"
    copy "$ASSETS/ci/ci-python.yml"                  "$TARGET/.github/workflows/ci.yml"
    ;;
  none) ;;
  *) echo "unknown stack: $STACK" >&2; exit 2 ;;
esac

echo "WRITTEN:"
printf '  %s\n' "${written[@]:-(none)}"
echo "SKIPPED (already present, left untouched):"
printf '  %s\n' "${skipped[@]:-(none)}"
```

- [ ] **Step 4: Make it executable and run the test**

Run:
```bash
chmod +x plugins/core/skills/setup-repo/scripts/scaffold-repo.sh
bash tests/setup-repo/test-scaffold.sh
```
Expected: ends with `ALL CHECKS PASSED` (with `ruff OK` / `pytest OK` if those tools are installed, else the "skipped" lines).

- [ ] **Step 5: Commit**

```bash
git add plugins/core/skills/setup-repo/scripts/scaffold-repo.sh tests/setup-repo/test-scaffold.sh
git commit -m "Add deterministic scaffold engine with end-to-end test"
```

---

### Task 5: The `setup-repo` SKILL.md procedure

**Files:**
- Create: `plugins/core/skills/setup-repo/SKILL.md`

**Interfaces:**
- Consumes: `scripts/scaffold-repo.sh` (Task 4) via `${CLAUDE_PLUGIN_ROOT}/skills/setup-repo/scripts/scaffold-repo.sh`.
- Produces: the model-invocable `core:setup-repo` skill.

- [ ] **Step 1: Write the SKILL.md**

`plugins/core/skills/setup-repo/SKILL.md`:
```markdown
---
name: setup-repo
description: Use when setting up a new or blank Offworld Labs repository, or when the user asks to "set up this repo per claude-shared", scaffold a repo to org standards, or add the standard Claude/CI/tooling setup. Scaffolds Claude Code enablement, review workflows, and stack tooling.
---

# Set up a repo per claude-shared

Scaffold the current repository to Offworld Labs standards: Claude Code
enablement, the Claude review workflows, and the chosen stack's tooling. The
mechanical file copying is done by the bundled engine; you handle the
interactive parts and the report.

`ENGINE="${CLAUDE_PLUGIN_ROOT}/skills/setup-repo/scripts/scaffold-repo.sh"`

## Procedure

1. **Confirm the target.** Ensure the working directory is a git repo
   (`git rev-parse --is-inside-work-tree`). If it is not, offer to run
   `git init`; abort if the user declines.

2. **Determine the stack.** Detect from existing files: `pyproject.toml` or
   `requirements*.txt` → `python`. If ambiguous or empty, ask the user to choose
   `python` or `none` (ts-frontend / ts-backend arrive in a later phase).

3. **Scaffold the files.** Run the engine, which never overwrites existing files:
   `bash "$ENGINE" . <stack>`
   Relay its `WRITTEN` / `SKIPPED` output to the user.

4. **Install dependencies.** For `python`, run
   `pip install -r requirements.txt -r requirements-dev.txt`
   (prefer an active virtualenv). Report the command and result; if the
   toolchain is unavailable, skip and note it rather than failing.

5. **Flesh out CLAUDE.md.** The stub was just written. Ask the user for a
   one-or-two-line description of what this repo does, then fill in the
   `Project Overview`, `Build & Test Commands`, and `Local Architecture`
   sections from their answer plus what was scaffolded (stack, `ruff check .`,
   `ruff format --check .`, `pytest`). If they skip, leave the stub as-is. Keep
   CLAUDE.md under the 200-line ceiling noted in the template.

6. **Report and follow-ups.** Summarise files written vs skipped, then list the
   manual steps: add the `CLAUDE_CODE_OAUTH_TOKEN` repo secret, and commit the
   workflows to the default branch before Claude review runs (see
   `docs/runbooks/github-actions-claude-review.md` for why). Do not commit on the
   user's behalf unless asked.
```

- [ ] **Step 2: Validate the plugin and skill frontmatter**

Run: `claude plugin validate ./plugins/core`
Expected: `Validation passed` (the `setup-repo` skill frontmatter parses; no YAML errors).

- [ ] **Step 3: Confirm the skill is discoverable**

Run:
```bash
claude plugin validate .
claude -p "List available skills whose name contains 'setup-repo'. Answer with just the namespaced skill name(s), or 'none'." --allowedTools "" 2>&1 | tail -3
```
Expected: `Validation passed`, and the model prints `core:setup-repo` (requires the plugin be installed/loadable; if it prints `none`, run `/reload-plugins` in an interactive session or reinstall `core@offworld` from the local marketplace first).

- [ ] **Step 4: Commit**

```bash
git add plugins/core/skills/setup-repo/SKILL.md
git commit -m "Add setup-repo skill procedure"
```

---

## Self-Review

**Spec coverage:**
- Delivery model (self-contained plugin, `${CLAUDE_PLUGIN_ROOT}`) → Tasks 1, 4, 5.
- Python defaults (ruff py312/120/EFW/double, pytest) → Task 2, verified in Tasks 2 & 4.
- Repo restructure (fold `templates/`+`rules/`, keep `docs/`) → Task 1.
- Rules copied not symlinked → Task 1 Step 2 + engine (Task 4).
- CI incl. write-permission workflows + `ci-python.yml` → Tasks 1, 3, 4.
- `.editorconfig` → Task 3.
- Procedure steps 1-9 (confirm, detect, enable, CI, stack, shared, install, flesh CLAUDE.md, report) → Task 5 (mechanical copying delegated to the engine, Task 4).
- Idempotent / non-clobber → engine `copy()` + Task 4 test.
- Testing (asset validity, temp-repo scaffold, ruff/pytest) → Tasks 2, 3, 4.
- Prerequisite (core at user scope) + adoption flow → Task 1 README rewrite.
- Out of scope confirmed: ts stacks (Phase 2), C++/pre-commit (Phase 3), governance.

**Placeholder scan:** none — every file's full contents and every command are inline.

**Type/name consistency:** engine signature `scaffold-repo.sh <target_dir> <stack>` with stacks `python|none`, dotfile renames `gitignore`→`.gitignore` / `editorconfig`→`.editorconfig`, and asset paths are identical across Tasks 1-5 and the tests.
```
