ZT-IAM Security Validation (Tamarin)
====================================

Scope
-----
This report validates the ZT-IAM authentication logic using formal proofs in Tamarin.
It covers: ZT-TOTP core, password + ZT-TOTP login, recovery codes, optional device
approval/WebAuthn, and the full authentication flow with fallbacks.

Environment
-----------
- Tamarin: 1.9.0 (container: `docker.io/flaminghoneybadger/tamarin`)
- Maude: 3.1 (bundled in container)
- Host: macOS arm64 (container runs linux/amd64)
- Project root: `<PROJECT_ROOT>`

Notation and Symbols
--------------------
- `u`: user, `d`: device, `rp`: relying party (RP)
- `pw`: password, `seed`: TOTP seed, `dk`: device key, `wk`: WebAuthn key
- `rcode`: recovery code, `n`: nonce, `t`: time step
- `Db(...)`: server-side state, `DeviceState(...)`: device state, `ChallengeState(...)`: pending challenge
- `DbRecovery(...)`: recovery code store, `WebAuthnState(...)`: WebAuthn device state
- Event labels (e.g., `Accept`, `AcceptPrimary`, `DeviceGenerated`) denote security-relevant steps

Results Summary
---------------
1) ZT-TOTP Core (`tamarin/zt_totp_core.spthy`)
   - `authentication`: verified
   - `seed_compromise_resisted`: verified

2) Password + ZT-TOTP Login (`tamarin/zt_totp_login.spthy`)
   - `password_and_device_required`: verified
   - `seed_compromise_resisted`: verified

3) Recovery Code (`tamarin/recovery_code.spthy`)
   - `recovery_requires_code`: verified
   - `recovery_resists_no_leak`: verified

4) Device Approval Optional (`tamarin/device_approval_optional.spthy`)
   - `approval_required_when_policy`: verified

5) Full Authentication (`tamarin/full_authentication.spthy`)
   - `primary_requires_password_and_device`: verified
   - `webauthn_enforced_when_required`: verified
   - `recovery_requires_code_issue`: verified
   - `seed_compromise_resisted`: verified

Interpretation
---------------------------------
- ZT‑TOTP core authentication is guaranteed: acceptance implies a device-generated
  proof, and OTP seed compromise alone is insufficient without device key compromise.
- Password + ZT‑TOTP login requires both password verification and device‑bound proof.
- Recovery login is only possible when a valid recovery code exists; no recovery
  succeeds without code disclosure.
- Optional device approval is enforced whenever the policy demands it.
- The full authentication model validates the end‑to‑end login with defined fallbacks.

Findings
------------------------------------
We formally validated the ZT-IAM authentication stack using Tamarin, covering ZT‑TOTP
core enrollment/verification, password + ZT‑TOTP login, recovery-code fallback, optional
device approval (WebAuthn policy), and the full end-to-end login flow. Across all models,
the core security claims are proven: successful authentication implies device-generated
proofs in addition to user secrets, and TOTP seed compromise alone cannot yield
acceptance without a corresponding device-key compromise. The recovery fallback is
proven to require issuance and disclosure of a valid recovery code, while WebAuthn is
enforced only when policy demands it. These results show that ZT‑TOTP strengthens
traditional TOTP deployments by binding OTP use to a device-held secret and the
intended RP, preserving usability while providing measurable resistance to seed
compromise and relay-style impersonation within the modeled threat assumptions.

Fallbacks by Factor
-------------------
- Password: required for primary login. Recovery bypass is only possible with a valid
  recovery code.
- ZT‑TOTP: required for primary login. Recovery bypass is only possible with a valid
  recovery code.
- WebAuthn: required only if policy mandates; otherwise optional in primary login.
- Recovery code: offline fallback; succeeds only if a valid code is present and not revoked.

Artifacts
---------
- Models: `tamarin/*.spthy`
- Results: `tamarin/results/*.txt`

Reproducibility
---------------
Run all proofs and capture outputs:

```
./scripts/run_tamarin_container.sh
```

Assumptions
-----------
- Device binding is modeled as a device‑held secret (`dk`) not available to the attacker.
- OTP generation is modeled as `h(<seed,time>)`.
- Network is Dolev‑Yao (attacker controls transport).

Limitations
-----------
- Abstract crypto (no concrete timing or hardware isolation).
- WebAuthn is modeled as a policy‑gated approval proof, not full FIDO2 semantics.
