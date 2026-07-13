#!/usr/bin/env bash
# One-liner entry for end users (from skill git / raw clone).
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/vidaudeveloper/creative-agent/main/tools/install-jy-compile.sh | bash
# or after clone:
#   bash tools/install-jy-compile.sh
set -euo pipefail

REPO_URL="${VIDAU_JY_COMPILER_REPO:-https://github.com/vidaudeveloper/creative-agent.git}"
REPO_REF="${VIDAU_JY_COMPILER_REF:-main}"

# If already inside a skill checkout that contains the compiler
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ -f "$HERE/jianying-draft-compiler/scripts/install_local.sh" ]]; then
  exec bash "$HERE/jianying-draft-compiler/scripts/install_local.sh"
fi

# Standalone: clone then install
CACHE="${VIDAU_JY_COMPILER_CACHE:-$HOME/.vidau/cache/creative-agent}"
mkdir -p "$(dirname "$CACHE")"
if [[ -d "$CACHE/.git" ]]; then
  git -C "$CACHE" fetch --depth 1 origin "$REPO_REF"
  git -C "$CACHE" checkout -q "$REPO_REF" 2>/dev/null || git -C "$CACHE" checkout -q "FETCH_HEAD"
  git -C "$CACHE" pull --ff-only origin "$REPO_REF" 2>/dev/null || true
else
  rm -rf "$CACHE"
  git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" "$CACHE"
fi

exec bash "$CACHE/tools/jianying-draft-compiler/scripts/install_local.sh"
