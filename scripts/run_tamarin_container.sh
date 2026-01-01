#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="${ROOT_DIR}/tamarin/results"
IMAGE="docker.io/flaminghoneybadger/tamarin"

mkdir -p "${RESULTS_DIR}"

run_model() {
  local model="$1"
  local out_file="${RESULTS_DIR}/${model}.txt"
  cat > "${out_file}" <<'EOF'
Notation
--------
u user, d device, rp relying party, pw password, seed TOTP seed, dk device key
wk WebAuthn key, rcode recovery code, n nonce, t time step
Db(...) server state, DeviceState(...) device state, ChallengeState(...) pending challenge
DbRecovery(...) recovery store, WebAuthnState(...) WebAuthn device state
Events include Accept, AcceptPrimary, AcceptRecovery, DeviceGenerated, WebAuthnApproved
EOF
  podman run --rm -v "${ROOT_DIR}:/workspace" -w /workspace \
    -e GHC_CHARENCODING=UTF-8 -e LANG=C.UTF-8 \
    --entrypoint tamarin-prover "${IMAGE}" \
    --prove --quiet "tamarin/${model}.spthy" >> "${out_file}"
}

run_model zt_totp_core
run_model zt_totp_login
run_model recovery_code
run_model device_approval_optional
run_model full_authentication

echo "Tamarin results written to ${RESULTS_DIR}"
