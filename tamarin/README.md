ZT-IAM Tamarin Models
=====================

This folder contains formal models for the ZT-IAM authentication flows. The models are
intended for research reporting and are structured as independent Tamarin theories.

Models
------
- `zt_totp_core.spthy`: ZT-TOTP core (device-bound proof + OTP + RP binding)
- `zt_totp_login.spthy`: password + ZT-TOTP login
- `recovery_code.spthy`: recovery-code login (offline access)
- `device_approval_optional.spthy`: optional device approval / WebAuthn step
- `full_authentication.spthy`: full login logic with password, ZT-TOTP, WebAuthn policy, and recovery fallback
- `trust_engine_policy.spthy`: multi-tenant trust engine policy evaluation (risk + step-up enforcement)
- `api_trust_engine.spthy`: API trust engine (rate-limit abuse + auto-suspension)

Notation
--------
- `u`: user, `d`: device, `rp`: relying party (RP)
- `pw`: password, `seed`: TOTP seed, `dk`: device-bound key, `wk`: WebAuthn key
- `rcode`: recovery code, `n`: server nonce, `t`: time step
- `Db(...)`: server-side state, `DeviceState(...)`: device state, `ChallengeState(...)`: pending challenge
- `DbRecovery(...)`: recovery code store, `WebAuthnState(...)`: WebAuthn device state
- Event labels (e.g., `Accept`, `AcceptPrimary`, `DeviceGenerated`) are security-relevant milestones used in lemmas

Running
-------
Install Tamarin Prover and run:

```
tamarin-prover tamarin/zt_totp_core.spthy
tamarin-prover tamarin/zt_totp_login.spthy
tamarin-prover tamarin/recovery_code.spthy
tamarin-prover tamarin/device_approval_optional.spthy
tamarin-prover tamarin/full_authentication.spthy
tamarin-prover tamarin/trust_engine_policy.spthy
tamarin-prover tamarin/api_trust_engine.spthy
```

Or use the helper script:

```
./scripts/run_tamarin.sh
```

Container run (no local install):

```
PROJECT_ROOT="<PROJECT_ROOT>"
podman run --rm -v "${PROJECT_ROOT}:/workspace" -w /workspace \
  -e GHC_CHARENCODING=UTF-8 -e LANG=C.UTF-8 \
  --entrypoint tamarin-prover docker.io/flaminghoneybadger/tamarin \
  --prove --quiet tamarin/zt_totp_core.spthy
```

Notes
-----
- These models intentionally abstract low-level crypto details to focus on security properties.
- Device binding is modeled as a device-held secret key (`dk`) that the server uses to validate proofs.
- OTP is modeled as `h(<seed,time>)` using the hashing builtin.
