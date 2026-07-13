#!/usr/bin/env bash
# Install jianying-draft-compiler for local Hermes / skill use.
# Default source: vidaudeveloper/creative-agent (tools/jianying-draft-compiler).
set -euo pipefail

TARGET="${VIDAU_JY_COMPILER_HOME:-$HOME/.vidau/jianying-draft-compiler}"
# Skill monorepo on GitHub (same repo users clone for skills)
REPO_URL="${VIDAU_JY_COMPILER_REPO:-https://github.com/vidaudeveloper/creative-agent.git}"
REPO_REF="${VIDAU_JY_COMPILER_REF:-main}"
COMPILER_SUBPATH="${VIDAU_JY_COMPILER_SUBPATH:-tools/jianying-draft-compiler}"
SRC_OVERRIDE="${VIDAU_JY_COMPILER_SRC:-}"

have_cmd() { command -v "$1" >/dev/null 2>&1; }

if ! have_cmd uv; then
  echo "Missing uv. Install: https://docs.astral.sh/uv/getting-started/installation/" >&2
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

if ! have_cmd git; then
  echo "Missing git." >&2
  exit 1
fi

resolve_src() {
  if [[ -n "$SRC_OVERRIDE" && -d "$SRC_OVERRIDE/src/jianying_draft_compiler" ]]; then
    echo "$SRC_OVERRIDE"
    return
  fi
  # This script lives in <compiler>/scripts/ when already inside a checkout
  local here
  here="$(cd "$(dirname "$0")/.." && pwd)"
  if [[ -d "$here/src/jianying_draft_compiler" ]]; then
    echo "$here"
    return
  fi
  # Skill repo root / tools/...
  if [[ -d "$here/../jianying-draft-compiler/src/jianying_draft_compiler" ]]; then
    echo "$(cd "$here/../jianying-draft-compiler" && pwd)"
    return
  fi
  local skill_root
  skill_root="$(cd "$(dirname "$0")/../../.." && pwd)"
  if [[ -d "$skill_root/tools/jianying-draft-compiler/src/jianying_draft_compiler" ]]; then
    echo "$skill_root/tools/jianying-draft-compiler"
    return
  fi
  if [[ -d "$HOME/Documents/project/creative-agent-skill/tools/jianying-draft-compiler/src/jianying_draft_compiler" ]]; then
    echo "$HOME/Documents/project/creative-agent-skill/tools/jianying-draft-compiler"
    return
  fi
  echo ""
}

clone_from_git() {
  local cache="${VIDAU_JY_COMPILER_CACHE:-$HOME/.vidau/cache/creative-agent}"
  mkdir -p "$(dirname "$cache")"
  if [[ -d "$cache/.git" ]]; then
    git -C "$cache" fetch --depth 1 origin "$REPO_REF"
    git -C "$cache" checkout -q "FETCH_HEAD" || git -C "$cache" checkout -q "$REPO_REF"
    git -C "$cache" pull --ff-only origin "$REPO_REF" 2>/dev/null || true
  else
    rm -rf "$cache"
    git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" "$cache"
  fi
  local src="$cache/$COMPILER_SUBPATH"
  if [[ ! -d "$src/src/jianying_draft_compiler" ]]; then
    echo "Repo cloned but missing $COMPILER_SUBPATH — check VIDAU_JY_COMPILER_SUBPATH" >&2
    exit 1
  fi
  echo "$src"
}

SRC="$(resolve_src)"
if [[ -z "$SRC" ]]; then
  echo "Local compiler not found; cloning $REPO_URL ($REPO_REF)…"
  SRC="$(clone_from_git)"
fi

mkdir -p "$(dirname "$TARGET")"
# Always materialize a stable home path (symlink to checkout)
if [[ "$(cd "$SRC" && pwd)" != "$(cd "$TARGET" 2>/dev/null && pwd || true)" ]]; then
  rm -rf "$TARGET"
  ln -sfn "$(cd "$SRC" && pwd)" "$TARGET"
fi

cd "$TARGET"
if [[ ! -d vendor/pyJianYingDraft ]]; then
  echo "WARNING: vendor/pyJianYingDraft missing — draft compile will fail." >&2
fi

uv sync
# Windows: install RPA export extras
if [[ "$(uname -s 2>/dev/null || echo unknown)" == MINGW* ]] \
  || [[ "$(uname -s 2>/dev/null || echo unknown)" == MSYS* ]] \
  || [[ "${OS:-}" == "Windows_NT" ]] \
  || [[ "$(python -c 'import sys; print(sys.platform)' 2>/dev/null || true)" == "win32" ]]; then
  echo "Installing Windows export extras…"
  uv sync --extra windows || uv pip install pywin32 pyautogui uiautomation || true
fi

BIN_DIR="$HOME/.vidau/bin"
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/jy-compile" <<EOF
#!/usr/bin/env bash
exec uv run --directory "$TARGET" jy-compile "\$@"
EOF
chmod +x "$BIN_DIR/jy-compile"

echo "OK: compiler at $TARGET (→ $(cd "$TARGET" && pwd -P 2>/dev/null || pwd))"
echo "CLI wrapper: $BIN_DIR/jy-compile"
echo "Add to PATH: export PATH=\"\$HOME/.vidau/bin:\$PATH\""
"$BIN_DIR/jy-compile" where || true
