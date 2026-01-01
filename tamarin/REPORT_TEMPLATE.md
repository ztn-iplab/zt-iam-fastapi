ZT-IAM Security Validation (Tamarin)
====================================

Project
-------
- System: ZT-IAM + ZT-Authenticator
- Model set: ZT-TOTP core, password+ZT-TOTP login, recovery codes, optional device approval

Environment
-----------
- Tamarin version:
- Host OS:
- Date:

Notation and Symbols
--------------------
- `u`: user, `d`: device, `rp`: relying party (RP)
- `pw`: password, `seed`: TOTP seed, `dk`: device key, `wk`: WebAuthn key
- `rcode`: recovery code, `n`: nonce, `t`: time step
- `Db(...)`: server-side state, `DeviceState(...)`: device state, `ChallengeState(...)`: pending challenge
- `DbRecovery(...)`: recovery code store, `WebAuthnState(...)`: WebAuthn device state
- Event labels (e.g., `Accept`, `AcceptPrimary`, `DeviceGenerated`) denote security-relevant steps

Models & Results
----------------
1) ZT-TOTP Core (`tamarin/zt_totp_core.spthy`)
   - Lemma: `authentication`
   - Lemma: `seed_compromise_resisted`
   - Result: PASS/FAIL
   - Notes:

2) Password + ZT-TOTP Login (`tamarin/zt_totp_login.spthy`)
   - Lemma: `password_and_device_required`
   - Lemma: `seed_compromise_resisted`
   - Result: PASS/FAIL
   - Notes:

3) Recovery Code (`tamarin/recovery_code.spthy`)
   - Lemma: `recovery_requires_code`
   - Lemma: `recovery_resists_no_leak`
   - Result: PASS/FAIL
   - Notes:

4) Device Approval Optional (`tamarin/device_approval_optional.spthy`)
   - Lemma: `approval_required_when_policy`
   - Result: PASS/FAIL
   - Notes:

5) Full Authentication (`tamarin/full_authentication.spthy`)
   - Lemma: `primary_requires_password_and_device`
   - Lemma: `webauthn_enforced_when_required`
   - Lemma: `recovery_requires_code_issue`
   - Lemma: `seed_compromise_resisted`
   - Result: PASS/FAIL
   - Notes:

Fallbacks (per factor)
----------------------
- Password: required for primary login; recovery bypasses password only with valid recovery code.
- ZT-TOTP: required for primary login; recovery bypasses ZT-TOTP only with valid recovery code.
- WebAuthn: required only if policy mandates; otherwise optional in primary login.
- Recovery code: offline fallback; succeeds only if a valid code is present and not revoked.

Assumptions
-----------
- Device binding is modeled as a device-held secret (`dk`) not available to the attacker.
- OTP generation is modeled as `h(<seed,time>)`.
- Transport channels are Dolev-Yao (adversary controls the network).

Threats Captured
----------------
- Seed compromise without device key
- Replay or relay across RP (RP binding in proof)
- Offline recovery-code misuse without code disclosure

Limitations
-----------
- Abstract crypto (no concrete timing, no hardware isolation details)
- WebAuthn modeled as optional approval (not full FIDO2)

Conclusion
----------
- Summary of proof results and implications for ZT-IAM security posture.
