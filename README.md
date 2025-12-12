# ZTN_SIM
# ZTN_SIM: Zero-Trust Identity & Access Management as a Service (IAMaaS)

ZTN_SIM is a Flask-based microservice for managing SIM card registration, user identities, and mobile-money operations with a Zero Trust approach. 
The service integrates JWT authentication, role-based access control, and logging, making it suitable for secure environments.
ZTN_SIM is a Flask-based, multi-tenant IAMaaS platform that originated as a telecom simulation lab to harden the SIM swap process before using a mobile number as a primary digital identity. The environment emulates carrier-grade flows (SIM lifecycle, KYC, wallet, and OTP) to enforce Zero Trust controls around who can perform SIM swaps and when. After securing the telecom layer, the same trusted identity can be federated into adjacent domains—government agencies, hospitals, banks, and other enterprises—without weakening the original safeguards.

## Features
The stack delivers tenant-isolated IAM with JWT-protected APIs, role-aware dashboards, WebAuthn/TOTP MFA, and per-tenant API key limits. Tenants authenticate via API keys, while users authenticate with tenant-scoped credentials, roles, and MFA backed by a device/IP-aware trust engine.

- **Flask application with modular blueprints** for authentication, wallets, transactions, roles, admin tasks, and WebAuthn endpoints.
- **JWT-based security with access** and refresh tokens stored in cookies for session continuity.
- **Role-based access control (RBAC)** allowing per-tenant user roles and access levels.
- **SIM card management** including registration and swap operations.
- **Wallet and transaction tracking** with fraud detection fields.
- **Email notifications and logging** for audit and alerting.
- **Docker and Docker Compose** support for containerized deployment.
## Core Capabilities
- **Multi-tenant RBAC**: `Tenant`, `TenantUser`, `UserRole`, and `UserAccessControl` models enforce tenant-specific roles and access levels.
- **Identity & SIM lifecycle**: User records link to SIM cards, wallets, transactions, OTP codes, and password history for full auditability.
- **Zero Trust controls**: Device/IP-aware trust engine, MFA enforcement per tenant, WebAuthn credentials, and detailed real-time logs.
- **Abuse protection**: API key rate limiting and automatic suspension backed by per-tenant score decay and request/error counters.
- **Deployment options**: Local Flask server or Docker Compose stack with Postgres and NGINX TLS termination.

## Project Structure
## Telecom Simulation & SIM Swap Defense
- **Carrier-grade flow modeling**: SIM lifecycle, wallet, OTP, and KYC artifacts mirror a telecom core so policies can be validated before production.
- **SIM swap safeguards**: Per-tenant MFA, device/IP trust scoring, password history, and OTP replay checks reduce SIM swap risk before a mobile number is elevated to a universal identity.
- **Identity federation**: Once a user passes telecom-grade checks, the same identity can be consumed by external relying parties (e.g., government, healthcare, finance) without relaxing controls; tenants can create isolated roles for each relying party.
- **Operational observability**: Real-time logs and risk scores surface who initiated a SIM swap, from where, and under which tenant—supporting post-incident forensics and automated lockdowns.

## Repository Layout
```
ZTN_SIM/
├── main.py               # Application entry point
├── config.py             # Configuration and environment variables
├── routes/               # Blueprint route handlers
├── models/               # SQLAlchemy models
├── utils/                # Helper utilities (logging, security, etc.)
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Compose file for app, DB, and NGINX
└── Dockerfile            # Image definition for the Flask app
├── main.py                 # Flask application factory and entrypoint
├── config.py               # Runtime configuration and environment bindings
├── routes/                 # Blueprints (auth, IAM API, roles, wallets, etc.)
├── models/                 # SQLAlchemy models, including tenant/RBAC entities
├── utils/                  # Security helpers (API keys, MFA, trust engine)
├── migrations/             # Alembic migrations for database schema
├── docker-compose.yml      # Postgres, app, and NGINX services
├── Dockerfile              # Production image for the Flask app
├── templates/ static/      # Dashboard views and assets
└── scripts: up.sh | stop.sh | pod.sh | gunicorn.sh
```

## Installation
## Runtime Configuration (.env)
Create a `.env` file in the project root. The values below are required for both local and containerized runs:

### Prerequisites
```
# Flask & JWT
JWT_SECRET_KEY=change-me
FLASK_SECRET_KEY=change-me-too

# Mail (used for alerts and password reset flows)
MAIL_USERNAME=your_gmail_username
MAIL_PASSWORD=your_app_password

- Python 3.10+
- PostgreSQL database
- Git
- (Optional) Docker and Docker Compose
# Database
# For local use the default in config.py or override here
SQLALCHEMY_DATABASE_URI=postgresql://ztn:ztn%40sim@localhost:5432/ztn_db
```

### Local Setup
Additional optional variables can be injected through `.env` and are read by `config.py` (for example, overriding JWT cookie behavior). The Docker Compose stack automatically loads this file for the application container.

1. Clone the repository and navigate into it:
## Local Development Quickstart
1. **Install prerequisites**: Python 3.10+, PostgreSQL 14+, and `pip`.
2. **Clone and bootstrap**:
   ```bash
   git clone <repo-url>
   cd ZTN_SIM
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file:
   ```env
   JWT_SECRET_KEY=your_jwt_secret
   FLASK_SECRET_KEY=your_flask_secret
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=app_specific_password
   ```
5. Initialize the database:
3. **Prepare environment**: create `.env` as shown above.
4. **Run database migrations**:
   ```bash
   flask db upgrade
   ```
6. Run the development server:
5. **Start the server** (development):
   ```bash
   python main.py
   ```
   The app serves HTTP on port 5000 by default.

### Running with Docker

1. Copy SSL certificates into `certs/` and private keys into `private/`.
2. Build and start the services:
## Docker Compose Deployment
1. Place TLS assets under `certs/` (public cert chain) and `private/` (matching keys). NGINX mounts these paths.
2. Ensure `.env` contains production-grade secrets. You can override the DB URI to `postgresql://ztn:ztn%40sim@db:5432/ztn_db` for in-cluster access.
3. Build and launch:
   ```bash
   ./up.sh
   ```
3. The app is exposed behind NGINX on port 443.
4. Access the app through NGINX on **https://localhost:443**. Stop the stack with `./stop.sh`.

To stop the services:
```bash
./stop.sh
```

## Key Configuration

- Database URL and other settings are configured in `config.py`.
- Logging writes to `logs/ztn_momo.log` via utilities under `utils/logger.py`.
- Default Docker image uses Python 3.10 and runs Gunicorn for production.
## Role Management & Dashboards

### Seed Default Roles and Admin
## Tenant Onboarding Runbook
All IAM APIs are protected by tenant API keys via the `X-API-Key` header (see `utils/api_key.py`). Use the Flask shell to create the first tenant, generate an API key, and seed initial roles.

After applying database migrations, seed the core roles and create an initial
admin account who can manage other users:

```bash
flask shell
```

```python
from models.models import db, User, UserRole, UserAccessControl
admin = User(
    email="admin@example.com", first_name="Admin", tenant_id=1,
    password="ChangeMe123", is_tenant_admin=True
)
db.session.add(admin); db.session.flush()

roles = {
    "admin": UserRole(role_name="admin", tenant_id=1),
    "agent": UserRole(role_name="agent", tenant_id=1),
    "user": UserRole(role_name="user", tenant_id=1),
}
db.session.add_all(roles.values()); db.session.flush()

db.session.add(UserAccessControl(
    user_id=admin.id, role_id=roles["admin"].id, tenant_id=1
))
db.session.commit()
exit()
```

### Adding Users and Promoting Agents

New sign-ups receive the `user` role and access the user dashboard. The admin
can promote a user to an agent either via the admin dashboard or role assignment API:

```bash
curl -X POST /roles/assign_role -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 2, "role_id": <agent_role_id>, "access_level": "write"}'
```

or by running the helper script:

```bash
python assign_roles.py
```

### Dashboards

- **Admin Dashboard** (`/admin/dashboard`): manage users and roles, review
  transactions, fund agents, inspect real-time logs, and administer tenants.
- **Agent Dashboard** (`/agent/dashboard`): register SIM cards, view registration
  history, and process withdrawals or transfers for customers.
- **User Dashboard** (`/user/dashboard`): view wallet balance, execute personal
  transfers or withdrawals, and manage profile information.
1. **Open the shell**:
   ```bash
   flask shell
   ```
2. **Create a tenant with an API key**:
   ```python
   from models.models import db, Tenant, User, UserRole, UserAccessControl, TenantUser
   from utils.api_key import generate_api_key

   tenant = Tenant(name="MasterTenant", contact_email="ops@example.com", plan="enterprise")
   tenant.api_key = generate_api_key()
   db.session.add(tenant); db.session.commit()
   print("API KEY:", tenant.api_key)
   ```
3. **Seed base roles for the tenant**:
   ```python
   roles = {
       "admin": UserRole(role_name="admin", tenant_id=tenant.id),
       "agent": UserRole(role_name="agent", tenant_id=tenant.id),
       "user": UserRole(role_name="user", tenant_id=tenant.id),
   }
   db.session.add_all(roles.values()); db.session.commit()
   ```
4. **Create a tenant admin user** (requires an existing SIM card tied to the `User`):
   ```python
   # Create the core user profile
   admin = User(email="admin@example.com", first_name="Admin", tenant_id=tenant.id)
   admin.password = "ChangeMe123"
   db.session.add(admin); db.session.flush()

   # Map the user into the tenant directory with a company email and login password
   tenant_user = TenantUser(
       tenant_id=tenant.id,
       user_id=admin.id,
       company_email="admin@example.com",
       password_hash=admin.password_hash,
       preferred_mfa="both"
   )
   db.session.add(tenant_user); db.session.flush()

   # Grant admin role and write access
   db.session.add(UserAccessControl(
       user_id=admin.id,
       tenant_id=tenant.id,
       role_id=roles["admin"].id,
       access_level="write"
   ))

   db.session.commit()
   ```
5. **(Optional) Import or create SIM cards** so tenants can register users by mobile number:
   ```python
   from models.models import SIMCard
   sim = SIMCard(iccid="8901234567890123456", mobile_number="250780000001", network_provider="MTN", status="active", user_id=admin.id)
   db.session.add(sim); db.session.commit()
   ```

By default, newly created users remain on the user dashboard until an admin
upgrades them to agent status.
## End-to-End Zero Trust Test (SIM Swap to External Reliance)
Use this flow to validate the platform as a Zero Trust IAMaaS offering and to demonstrate how a telecom-grade identity can be reused by external tenants.

1. **Bootstrap a telecom tenant** using the runbook above and ensure MFA is required (`preferred_mfa="both"`).
2. **Create a SIM swap scenario**:
   - Insert a SIM record tied to the target user.
   - Trigger a SIM swap by rotating the associated `SIMCard.status` to `pending_swap`, issuing an OTP, and logging the event via `RealTimeLog`.
   - Verify the trust engine (IP/device metadata) and OTP replay protection reject untrusted swap attempts.
3. **Attest the identity** once the swap is approved: capture the user’s WebAuthn credential or OTP proof and mark the SIM card `active`.
4. **Provision an external relying tenant** (e.g., a hospital): create a second tenant, generate its API key, and map the previously attested user into that tenant with a scoped role (e.g., `hospital_patient`).
5. **Call IAM APIs as the relying tenant** using the new API key and user JWT to confirm cross-tenant federation works without bypassing telecom safeguards.
6. **Inspect observability**: view `RealTimeLog` entries to confirm who initiated each step, which tenant was involved, and whether risk scores triggered any lockdowns.

## Calling IAM APIs
- **Headers**: every IAM request must include `X-API-Key: <tenant_api_key>`. JWTs returned by login are used for subsequent protected calls.
- **Registration** (`POST /api/v1/auth/register`): create a tenant user by mobile number and company email. Defaults to `user` role unless `role` is supplied.
- **Login** (`POST /api/v1/auth/login`): supports username/email or mobile number. Trust engine logs IP/device metadata; MFA preferences are enforced per tenant.
- **Role assignment**: use `/roles/assign_role` endpoints or run `python assign_roles.py` to batch-assign roles for a tenant.
- **Dashboards**: `/admin/dashboard`, `/agent/dashboard`, and `/user/dashboard` render tenant-aware views for administrators, agents, and end users respectively.

Refer to `openapi.yaml` and the blueprints under `routes/` for the full API surface and payload schemas.

## Logging, Auditing, and Security
- **Real-time logs** (`RealTimeLog`) capture tenant, user, action, IP, device, and risk flags.
- **Abuse detection**: API key usage contributes to `api_score`; crossing the block threshold automatically suspends the tenant key.
- **Authentication history**: `UserAuthLog`, `PasswordHistory`, and `TenantPasswordHistory` track sign-ins and password rotations.
- **MFA & WebAuthn**: tenant policies can require strict MFA and store WebAuthn credentials with per-tenant uniqueness.

## Troubleshooting
- Verify the database connection in `config.py` if migrations fail.
- Missing or invalid `X-API-Key` will yield `401/403` errors before hitting handlers.
- If rate limits trip, clear `api_score`, `api_request_count`, and `api_error_count` for the tenant via the Flask shell after confirming the cause.

## License

This project is released under the MIT License. See `LICENSE` for details.
Released under the MIT License. See `LICENSE` for details.
