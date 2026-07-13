#!/usr/bin/env bash
# Hermes / agent helper: ensure jy-compile is on PATH.
set -euo pipefail

export PATH="${HOME}/.vidau/bin:${PATH}"

if command -v jy-compile >/dev/null 2>&1; then
  echo "jy-compile: $(command -v jy-compile)"
  jy-compile where || true
  exit 0
fi

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
# creative-agent-skill repo root when this file is at L1-capability/jianying-remix/scripts/
CANDIDATES=(
  "${VIDAU_JY_COMPILER_SRC:-}"
  "${ROOT}/tools/jianying-draft-compiler"
  "${ROOT}/../jianying-draft-compiler"
  "${HOME}/Documents/project/creative-agent-skill/tools/jianying-draft-compiler"
  "${HOME}/Documents/project/jianying-draft-compiler"
  "${HOME}/.vidau/jianying-draft-compiler"
)

SRC=""
for c in "${CANDIDATES[@]}"; do
  [[ -z "$c" ]] && continue
  if [[ -f "$c/scripts/install_local.sh" ]]; then
    SRC="$c"
    break
  fi
done

if [[ -n "$SRC" ]]; then
  bash "$SRC/scripts/install_local.sh"
else
  # Fall back to GitHub skill monorepo
  echo "Local compiler missing; installing from GitHub…"
  bash "${ROOT}/tools/install-jy-compile.sh" 2>/dev/null \
    || curl -fsSL "https://raw.githubusercontent.com/vidaudeveloper/creative-agent/${VIDAU_JY_COMPILER_REF:-main}/tools/install-jy-compile.sh" | bash
fi

export PATH="${HOME}/.vidau/bin:${PATH}"
jy-compile where
