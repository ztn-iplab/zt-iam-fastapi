#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THEORY_DIR="${ROOT_DIR}/tamarin"
RESULTS_DIR="${THEORY_DIR}/results"

if ! command -v tamarin-prover >/dev/null 2>&1; then
  echo "tamarin-prover not found in PATH."
  echo "Install it and re-run this script."
  exit 1
fi

mkdir -p "${RESULTS_DIR}"

run_model() {
  local model="$1"
  local out_file="${RESULTS_DIR}/${model}.txt"
  cat > "${out_file}" <<'EOF'
Notation
--------
u user, d device, rp relying party, pw password, seed TOTP seed, dk device key
wk WebAuthn key, rcode recovery code, n nonce, t time step
t tenant, r request, policy policy flag, score API score
Db(...) server state, DeviceState(...) device state, ChallengeState(...) pending challenge
DbRecovery(...) recovery store, WebAuthnState(...) WebAuthn device state
Events include Accept, AcceptPrimary, AcceptRecovery, DeviceGenerated, WebAuthnApproved
EOF
  tamarin-prover "${THEORY_DIR}/${model}.spthy" >> "${out_file}"
}

run_model zt_totp_core
run_model zt_totp_login
run_model recovery_code
run_model device_approval_optional
run_model full_authentication
run_model trust_engine_policy
run_model api_trust_engine

echo "Tamarin results written to ${RESULTS_DIR}"
