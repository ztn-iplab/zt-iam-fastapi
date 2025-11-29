# ZTN_SIM API Reference

This document consolidates the public and internal API surface exposed by the Flask application. It groups endpoints by blueprint, clarifies authentication, and highlights notable side effects (logging, trust scoring, or MFA requirements). The interface is versioned (`/api/v1/auth` for IAMaaS) and mirrored in the OpenAPI 3.0 schema so external systems can contract-test against the same definitions used by the `auth-gateway` and policy decision point.

## Machine-Readable Contract & Tooling
- **OpenAPI 3.0 schema:** Serves as the canonical contract for request/response types, error codes, auth headers, and rate limits, enabling static analysis and contract testing before deployment.
- **Client generation:** Tested with auto-generated clients (Python, JavaScript, Go) to validate that the documented interface is executable and self-consistent during integration and load exercises.
- **Developer tooling:** The schema can be consumed by Swagger UI, Postman collections, and AI-assisted code-completion tools to propose correctly structured API calls and error-handling patterns, reducing integration friction.
- **Versioning:** Stable, versioned endpoints support staged pilots for external partners (e.g., HMS, MNOs) using synthetic identifiers to exercise trust-score behaviors around SIM lifecycle events, device changes, and policy variations without exposing production data.

## Conventions
- **Base URLs:** Most dashboards and wallet/transaction endpoints are mounted at `/`. The IAMaaS tenant APIs are mounted under `/api/v1/auth`.
- **Authentication:**
  - JWT access tokens are expected via the `Authorization: Bearer <token>` header for protected routes unless noted otherwise.
  - IAMaaS endpoints also require `X-API-Key` for tenant scoping.
  - Some OTP and WebAuthn flows rely on server-managed sessions for challenge state.
- **MFA:** TOTP (`/setup-totp`, `/verify-totp` variants) and WebAuthn endpoints enforce additional verification during login, password reset, or tenant policy changes.
- **Logging & Trust:** Authentication and transaction flows log to `RealTimeLog` and calculate trust scores to flag risk or lock accounts when thresholds are exceeded.

## Identity & Tenant IAM (`/api/v1/auth`)
| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/register` | X-API-Key | Register an existing SIM user under the calling tenant, assign role/access level, and log registration. |
| POST | `/login` | X-API-Key | Tenant-scoped login that records auth attempts, evaluates trust score, resolves tenant role, and returns a JWT with MFA directives. |
| POST | `/forgot-password` | X-API-Key | Request a password reset email with a tenant-scoped token (logs the event and hashes the token). |
| POST | `/reset-password` | X-API-Key | Complete password reset with strength checks, trust gating, and optional WebAuthn/TOTP verification based on configured MFA. |
| GET | `/enroll-totp` | X-API-Key | Provide a QR-code image (base64) to enroll a TOTP secret for the tenant user. |
| POST | `/setup-totp/confirm` | X-API-Key | Confirm TOTP enrollment by verifying a passcode and storing the secret. |
| POST | `/verify-totp-login` | JWT + X-API-Key | Validate TOTP during login when required by risk level or tenant policy. |
| POST | `/request-totp-reset` | X-API-Key | Email a TOTP reset token with rate limiting; logs administrative alerts. |
| POST | `/verify-totp-reset` | X-API-Key | Validate the TOTP reset token before updating secrets. |
| POST | `/verify-fallback-totp` | X-API-Key | Verify backup TOTP codes for break-glass scenarios. |
| POST | `/request-reset-totp` | X-API-Key | Initiate TOTP reset with tenant-level notification controls. |
| POST | `/verify-totp-reset` | X-API-Key | Confirm reset and allow MFA reconfiguration. |
| POST | `/webauthn/register-begin` | X-API-Key | Begin WebAuthn registration (returns challenge options encoded for JSON). |
| POST | `/webauthn/register-complete` | X-API-Key | Finalize WebAuthn registration and persist credentials. |
| POST | `/webauthn/assertion-begin` | X-API-Key | Begin a WebAuthn assertion during login. |
| POST | `/webauthn/assertion-complete` | X-API-Key | Complete WebAuthn assertion; may be used for high-trust logins. |
| POST | `/webauthn/reset-assertion-begin` | X-API-Key | Start WebAuthn recovery for password reset. |
| POST | `/webauthn/reset-assertion-complete` | X-API-Key | Finish WebAuthn recovery for password reset. |
| POST | `/logout` | JWT + X-API-Key | Invalidate the current session token. |
| POST | `/refresh` | JWT + X-API-Key | Refresh the JWT when a valid refresh token/cookie is present. |
| GET | `/health-check` | None | Lightweight service probe. |
| GET | `/trust-score` | JWT + X-API-Key | Return the current user trust score for the tenant. |
| POST | `/out-request-webauthn-reset` | X-API-Key | Send an out-of-band WebAuthn reset email containing a token. |
| POST | `/out-verify-webauthn-reset/<token>` | X-API-Key | Validate the emailed reset token before WebAuthn reset. |
| GET/POST | `/tenant/roles` | JWT + X-API-Key | List or create tenant-specific roles. |
| GET/POST/PUT/DELETE | `/tenant/users` | JWT + X-API-Key | CRUD for tenant user mappings, including role assignments and suspension/deletion. |
| PUT | `/tenant/users/<user_id>` | JWT + X-API-Key | Update tenant user details or status. |
| GET | `/tenant/users/<user_id>` | JWT + X-API-Key | Retrieve tenant user details with access controls. |
| GET/PUT | `/tenant-settings` | JWT + X-API-Key | Read or modify tenant security/plan settings (e.g., enforce strict MFA). |
| POST | `/change-plan` | JWT + X-API-Key | Change tenant plan, impacting API limits. |
| GET | `/tenant/system-metrics` | JWT + X-API-Key | Tenant-level usage and health metrics. |
| POST/GET/PUT/DELETE | `/tenant/trust-policy*` | JWT + X-API-Key | Upload, view, edit, or clear trust policy files used by the risk engine. |
| PUT | `/tenant/user/preferred-mfa` | JWT + X-API-Key | Set user-preferred MFA method with policy enforcement. |
| GET/PUT | `/tenant/mfa-policy` | JWT + X-API-Key | View or update MFA policy requirements for the tenant. |

## Core Auth (Web) (`routes/auth.py`)
These routes back the web experience and cookies-based JWT sessions.
- **Login & registration:** `/login`, `/register` (JSON POST) plus form-rendering helpers (`/login_form`, `/register_form`).
- **MFA enrollment and verification:** `/setup-totp`, `/setup-totp/confirm`, `/verify-totp`, `/verify-fallback_totp`, `/preferred-mfa` (GET/PUT).
- **Session management:** `/whoami`, `/refresh`, `/logout`, `/debug-cookie`.
- **Password lifecycle:** `/forgot-password`, `/reset-password`, `/change-password` with trust gating and history checks.
- **WebAuthn recovery:** `/request-reset-webauthn`, `/out-request-webauthn-reset`, `/out-verify-webauthn-reset/<token>`.
- **SIM swap verification:** `/verify-sim-swap` requires OTP to approve pending swaps.

## User Routes (`routes/user_routes.py`)
| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/user/dashboard` | JWT | Render user dashboard template. |
| POST | `/users` | Open | Create a new user record. |
| GET/PUT/DELETE | `/user` | JWT | Retrieve, update, or delete the authenticated user. |
| GET | `/user/profile` | JWT | Return profile details for the logged-in user. |
| POST | `/user/request_deletion` | JWT | Initiate account deletion workflow. |
| GET | `/user-info/<mobile_number>` | JWT | Lookup user by SIM/mobile number. |
| GET | `/setup-totp` | JWT | Fetch QR for TOTP setup (user context). |

## Wallet Routes (`routes/wallet_routes.py`)
| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/wallets` | JWT | List wallets or retrieve current balance. |
| PUT | `/wallets` | JWT | Update wallet details (e.g., freeze state or metadata). |
| DELETE | `/wallets` | JWT | Remove a wallet association. |

## Transaction Routes (`routes/transaction_routes.py`)
| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/transactions` | JWT + session_protected | Create a transfer or withdrawal with TOTP verification, risk scoring, and fraud logging. |
| GET | `/transactions` | JWT | List transactions for the authenticated user with optional filters. |
| PUT | `/transactions/<transaction_id>` | JWT | Update transaction status/details (e.g., approval). |
| DELETE | `/transactions/<transaction_id>` | JWT | Delete/cancel a transaction. |
| POST | `/user/initiated-withdrawal` | JWT | Begin a withdrawal that awaits agent approval. |
| POST | `/verify-transaction-otp` | JWT | Verify OTP for sensitive transactions. |

## Roles Routes (`routes/roles_routes.py`)
- `GET /roles` – List all roles.
- `GET /user/<user_id>` – Fetch roles for a specific user.
- `POST /assign_role` – Assign a role with access level to a user.

## Agent Routes (`routes/agent_routes.py`)
Operational endpoints for agents managing SIMs and customer operations.
- SIM lifecycle: `/agent/generate_sim` (create SIM), `/agent/register_sim`, `/agent/view_sim/<iccid>`, `/agent/activate_sim`, `/agent/suspend_sim`, `/agent/reactivate_sim`, `/agent/delete_sim`.
- Dashboard and data: `/agent/dashboard`, `/agent/dashboard/data`, `/agent/profile`.
- Transactions: `/agent/transaction` (process), `/agent/transactions` (list), `/agent/pending-withdrawals`, `/agent/approve-withdrawal/<id>`, `/agent/reject-withdrawal/<id>`.
- Wallet: `/agent/wallet` (view balance and operations).
- SIM swap: `/agent/request-sim-swap` initiates swap workflow with OTP verification.

## Admin Routes (`routes/admin_routes.py`)
Administrative endpoints for user, tenant, and finance operations.
- Dashboards: `/admin/dashboard`.
- User management: `/admin/users` (list), `/admin/assign_role`, `/admin/suspend_user/<id>`, `/admin/verify_user/<id>`, `/admin/delete_user/<id>`, `/admin/edit_user/<id>`, `/admin/view_user/<id>`, `/admin/unlock-user/<id>`.
- SIM generation: `/admin/generate_sim` (GET form to create SIMs for users/agents).
- Agent funding & float: `/admin/fund-agent`, `/admin/hq-balance`, `/admin/float-history`.
- Monitoring: `/admin/flagged-transactions`, `/admin/real-time-logs`, `/admin/user-auth-logs`, `/admin/all-transactions`, `/api/admin/metrics` (JSON metrics feed).
- Transaction remediation: `/admin/reverse-transfer/<transaction_id>`.
- Tenant lifecycle: `/admin/register-tenant`, `/admin/rotate-api-key/<tenant_id>`, `/admin/tenants`, `/admin/toggle-tenant/<tenant_id>`, `/admin/delete-tenant/<tenant_id>`, `/admin/update-tenant/<tenant_id>`, `/admin/reset-trust-score/<tenant_id>`, `/admin/tenant-details/<tenant_id>`.

## Settings Routes (`routes/settings_routes.py`)
- `GET /` (index) – Render settings landing page.
- `GET /change-password` – Serve password change UI.
- `GET /reset-totp` – Start TOTP reset flow.
- `GET /reset-webauthn` – Start WebAuthn reset flow.
- `POST /settings/update-profile` – Persist profile updates.
- `POST /settings/request-deletion` – Trigger account deletion request.

## WebAuthn Routes (`routes/webauthn.py`)
WebAuthn support for the primary web experience (separate from IAMaaS tenant APIs).
- Registration: `/webauthn/register-begin`, `/webauthn/register-complete`.
- Assertion: `/webauthn/assertion` (UI), `/webauthn/assertion-begin`, `/webauthn/assertion-complete`.
- Recovery: `/webauthn/reset-assertion-begin`, `/webauthn/reset-assertion-complete`.

## Integration Notes
- **API keys**: Tenants generate and rotate keys via admin endpoints; include `X-API-Key` on all `/api/v1/auth` calls.
- **JWT handling**: Use bearer tokens for API clients; web flows rely on cookies set by Flask-JWT-Extended helper functions.
- **TOTP delivery**: TOTP enrollment endpoints return QR images as base64 strings for authenticator apps.
- **Rate limits & abuse**: API keys are rate-limited per plan and can be auto-suspended by the trust engine for excess errors or requests.
