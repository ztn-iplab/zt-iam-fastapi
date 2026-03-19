#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="${ROOT_DIR}/tamarin/results"
MODEL="aig_actor_integrity"
IMAGE="${TAMARIN_IMAGE:-docker.io/flaminghoneybadger/tamarin}"
OUT_FILE="${RESULTS_DIR}/${MODEL}.txt"

mkdir -p "${RESULTS_DIR}"

{
  echo "AIg Actor Integrity Proof"
  echo "------------------------"
  echo "Model: tamarin/${MODEL}.spthy"
  echo "Date (UTC): $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo
} > "${OUT_FILE}"

if command -v tamarin-prover >/dev/null 2>&1; then
  tamarin-prover --prove --quiet "${ROOT_DIR}/tamarin/${MODEL}.spthy" >> "${OUT_FILE}"
else
  podman run --rm -v "${ROOT_DIR}:/workspace" -w /workspace \
    -e GHC_CHARENCODING=UTF-8 -e LANG=C.UTF-8 \
    --entrypoint tamarin-prover "${IMAGE}" \
    --prove --quiet "tamarin/${MODEL}.spthy" >> "${OUT_FILE}"
fi

python3 - "${OUT_FILE}" "${ROOT_DIR}" <<'PY'
from pathlib import Path
import sys

out_file = Path(sys.argv[1])
root_dir = sys.argv[2]
text = out_file.read_text(encoding="utf-8")
text = text.replace(root_dir, "<PROJECT_ROOT>")
out_file.write_text(text, encoding="utf-8")
PY

echo "Wrote ${OUT_FILE}"
