#!/usr/bin/env bash
# Sync pyJianYingDraft + draft template from a local capcut-mate checkout.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MATE="${CAPCUT_MATE_ROOT:-$(cd "$ROOT/../capcut-mate" && pwd)}"

if [[ ! -d "$MATE/src/pyJianYingDraft" ]]; then
  echo "capcut-mate not found at: $MATE" >&2
  echo "Set CAPCUT_MATE_ROOT to the mate repo path." >&2
  exit 1
fi

rm -rf "$ROOT/vendor/pyJianYingDraft" "$ROOT/vendor/template_default2"
cp -R "$MATE/src/pyJianYingDraft" "$ROOT/vendor/pyJianYingDraft"
cp -R "$MATE/template/default2" "$ROOT/vendor/template_default2"
find "$ROOT/vendor" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

echo "Synced vendor from $MATE"
