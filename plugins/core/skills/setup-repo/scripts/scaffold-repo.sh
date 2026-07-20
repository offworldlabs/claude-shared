#!/usr/bin/env bash
# Deterministic file-scaffolding engine for the core:setup-repo skill.
# Copies bundled assets into a target repo without clobbering existing files.
# Usage: scaffold-repo.sh <target_dir> <stack>
#   <stack>: python | ts-frontend | ts-backend | none
set -euo pipefail

TARGET="${1:?target dir required}"
STACK="${2:-none}"
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../assets" && pwd)"

case "$STACK" in
  python|ts-frontend|ts-backend|none) ;;
  *) echo "unknown stack: $STACK" >&2; exit 2 ;;
esac

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
  ts-frontend)
    copy "$ASSETS/stack/ts-frontend/package.json"     "$TARGET/package.json"
    copy "$ASSETS/stack/ts-frontend/tsconfig.json"    "$TARGET/tsconfig.json"
    copy "$ASSETS/stack/ts-frontend/eslint.config.js" "$TARGET/eslint.config.js"
    copy "$ASSETS/stack/ts-frontend/vitest.config.ts" "$TARGET/vitest.config.ts"
    copy "$ASSETS/stack/ts-frontend/gitignore"        "$TARGET/.gitignore"
    copy "$ASSETS/stack/ts-frontend/src/index.ts"      "$TARGET/src/index.ts"
    copy "$ASSETS/stack/ts-frontend/src/index.test.ts" "$TARGET/src/index.test.ts"
    copy "$ASSETS/ci/ci-node.yml"                     "$TARGET/.github/workflows/ci.yml"
    ;;
  ts-backend)
    copy "$ASSETS/stack/ts-backend/package.json"      "$TARGET/package.json"
    copy "$ASSETS/stack/ts-backend/tsconfig.json"     "$TARGET/tsconfig.json"
    copy "$ASSETS/stack/ts-backend/eslint.config.js"  "$TARGET/eslint.config.js"
    copy "$ASSETS/stack/ts-backend/vitest.config.ts"  "$TARGET/vitest.config.ts"
    copy "$ASSETS/stack/ts-backend/gitignore"         "$TARGET/.gitignore"
    copy "$ASSETS/stack/ts-backend/src/index.ts"       "$TARGET/src/index.ts"
    copy "$ASSETS/stack/ts-backend/src/index.test.ts"  "$TARGET/src/index.test.ts"
    copy "$ASSETS/ci/ci-node.yml"                     "$TARGET/.github/workflows/ci.yml"
    ;;
  none) ;;
esac

echo "WRITTEN:"
printf '  %s\n' "${written[@]:-(none)}"
echo "SKIPPED (already present, left untouched):"
printf '  %s\n' "${skipped[@]:-(none)}"
