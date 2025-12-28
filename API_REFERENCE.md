# ZT-IAM API Reference

This document consolidates the public and internal API surface exposed by ZT-IAM. It groups endpoints by router, clarifies authentication, and highlights notable side effects (logging, trust scoring, or MFA requirements). The interface is treated as a versioned REST contract (`/api/v1/auth` for tenant IAM) and is mirrored in a machine-readable OpenAPI 3.0 schema so external systems and internal components share the same request/response definitions for authentication, token issuance, trust-score inspection, policy management, and audit retrieval.

## Machine-Readable Contract & Tooling
- **OpenAPI 3.0 schema (present):** `openapi.yaml` is the canonical contract for request/response types, error codes, auth headers, and rate limits.
- **Client generation:** Use `openapi-generator-cli` to generate clients for Python/JS/Go.
- **Developer tooling:** Swagger UI, Postman collections, and IDE tooling can consume the schema for accurate requests and error handling.
- **Versioning:** Stable, versioned endpoints under `/api/v1/auth` support external tenants and staged rollouts.

## Conventions
- **Base URLs:** Dashboards and core routes are mounted at `/`. Tenant IAM APIs are mounted under `/api/v1/auth`.
- **Authentication:**
  - Web flows use cookie-based JWTs.
  - Tenant APIs require `X-API-Key` and may also include JWTs for tenant user actions.
- **MFA:** TOTP and WebAuthn are enforced based on trust and policy.
- **Logging & Trust:** Auth and transaction flows log to `RealTimeLog` and update trust scores.

## Tenant IAM (`/api/v1/auth`)
| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/register` | X-API-Key | Register a SIM-linked user under the tenant. |
| POST | `/login` | X-API-Key | Tenant-scoped login with trust scoring and MFA directives. |
| POST | `/forgot-password` | X-API-Key | Request tenant password reset (email link). |
| POST | `/reset-password` | X-API-Key | Complete password reset with MFA gates. |
| GET | `/enroll-totp` | X-API-Key | Provide QR to enroll TOTP. |
| POST | `/setup-totp/confirm` | X-API-Key | Confirm TOTP enrollment. |
| POST | `/verify-totp-login` | JWT + X-API-Key | Validate TOTP during login. |
| POST | `/request-totp-reset` | X-API-Key | Email TOTP reset link. |
| POST | `/verify-totp-reset` | X-API-Key | Verify TOTP reset token. |
| POST | `/verify-fallback-totp` | X-API-Key | Verify backup TOTP codes. |
| POST | `/webauthn/register-begin` | X-API-Key | Begin WebAuthn registration. |
| POST | `/webauthn/register-complete` | X-API-Key | Finalize WebAuthn registration. |
| POST | `/webauthn/assertion-begin` | X-API-Key | Begin WebAuthn assertion. |
| POST | `/webauthn/assertion-complete` | X-API-Key | Complete WebAuthn assertion. |
| POST | `/webauthn/reset-assertion-begin` | X-API-Key | Begin WebAuthn recovery. |
| POST | `/webauthn/reset-assertion-complete` | X-API-Key | Complete WebAuthn recovery. |
| POST | `/logout` | JWT + X-API-Key | Invalidate session token. |
| POST | `/refresh` | JWT + X-API-Key | Refresh access token. |
| GET | `/trust-score` | JWT + X-API-Key | Retrieve trust score. |
| PUT | `/tenant/user/preferred-mfa` | JWT + X-API-Key | Update tenant user MFA preference. |

## Core Auth (Web)
- **Login & registration:** `/api/auth/login`, `/api/auth/register` plus forms `/api/auth/login_form`, `/api/auth/register_form`.
- **MFA enrollment:** `/api/auth/setup-totp`, `/api/auth/setup-totp/confirm`, `/api/auth/verify-totp`, `/api/auth/verify-totp-login`.
- **WebAuthn:** `/webauthn/*` for browser-based registration and assertions.
- **Password lifecycle:** `/api/auth/forgot-password`, `/api/auth/reset-password`, `/api/auth/change-password`.
- **Session:** `/api/auth/refresh`, `/api/auth/logout`.

## User Routes
| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/user/dashboard` | JWT | Render user dashboard. |
| POST | `/users` | JWT | Create user record. |
| GET/PUT/DELETE | `/user` | JWT | Retrieve/update/delete authenticated user. |
| GET | `/user/profile` | JWT | Fetch profile details. |
| POST | `/user/request_deletion` | JWT | Request deletion. |
| GET | `/user-info/<mobile_number>` | JWT | Lookup by SIM/mobile number. |

## Agent Routes
Operational endpoints for agents managing SIMs and transactions.
- `/agent/dashboard`, `/agent/dashboard/data`, `/agent/profile`
- `/agent/transaction`, `/agent/transactions`
- SIM lifecycle: `/agent/generate_sim`, `/agent/register_sim`, `/agent/view_sim/<iccid>`, `/agent/activate_sim`, `/agent/suspend_sim`, `/agent/reactivate_sim`, `/agent/delete_sim`
- SIM swap: `/agent/request-sim-swap`

## Admin Routes
Administrative endpoints for users, tenants, and risk operations.
- `/admin/dashboard`, `/admin/users`, `/admin/view_user/<id>`, `/admin/edit_user/<id>`
- Role and access: `/admin/assign_role`, `/admin/verify_user/<id>`, `/admin/suspend_user/<id>`, `/admin/unlock-user/<id>`
- Tenant lifecycle: `/admin/register-tenant`, `/admin/rotate-api-key/<id>`, `/admin/tenants`, `/admin/update-tenant/<id>`, `/admin/toggle-tenant/<id>`, `/admin/delete-tenant/<id>`
- Monitoring: `/admin/flagged-transactions`, `/admin/real-time-logs`, `/admin/user-auth-logs`, `/admin/all-transactions`

## Settings Routes
- `/settings` (modal), `/settings/change-password`, `/settings/reset-totp`, `/settings/reset-webauthn`
- `/settings/update-profile`, `/settings/request-deletion`

## WebAuthn (Web)
- `/webauthn/register-begin`, `/webauthn/register-complete`
- `/webauthn/assertion-begin`, `/webauthn/assertion-complete`
- `/webauthn/reset-assertion-begin`, `/webauthn/reset-assertion-complete`
