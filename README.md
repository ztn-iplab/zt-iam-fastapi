# ZT-IAM

ZT-IAM is a FastAPI-based Zero Trust IAM platform with tenant-aware RBAC, MFA (TOTP + WebAuthn), SIM lifecycle controls, wallet/transaction flows, and audit-grade logging. It is designed to enforce strong identity assurances before a mobile number becomes a trusted identifier across external services.

## Highlights
- **Multi-tenant IAM** with tenant-scoped roles and access controls.
- **MFA enforcement** with TOTP and WebAuthn, plus device/IP trust scoring.
- **SIM lifecycle & swap safeguards** with approval flows and audit trails.
- **Wallet + transaction tracking** with fraud/risk metadata.
- **Admin, agent, and user dashboards** with role-enforced actions.
- **JWT auth** using secure cookies and refresh tokens.

## ZT-Authenticator Enrollment
ZT-IAM issues a **ZT-Authenticator enrollment QR** instead of standard otpauth URIs.

1) Log in and open **Set Up TOTP**.
2) Scan the QR with the ZT-Authenticator app (device-bound enrollment).
3) Approve logins in ZT-Authenticator when prompted.

If QR scan is not possible, the setup page shows an **enrollment link** you can paste into the app.

ZT-Authenticator API base URL (for QR/link payloads):
```
https://<your-domain>/api/auth
```

## Repository Layout
```
ZT-IAM/
├── app/                   # FastAPI routers, models, auth, security
├── templates/             # Dashboard and auth HTML
├── static/                # JS/CSS assets
├── migrations/            # Alembic migrations
├── scripts/               # Seed + helper scripts
├── nginx/                 # NGINX config
├── docker-compose.yml     # App + Postgres + NGINX + Mailpit
├── Dockerfile             # Production image
├── fastapi_app.py         # ASGI entrypoint
└── run.sh                 # Helper to start the stack
```

## Configuration (.env)
Create a `.env` file in the project root (required):
```env
JWT_SECRET_KEY=your-strong-secret
FLASK_SECRET_KEY=your-strong-secret
SQLALCHEMY_DATABASE_URI=postgresql://ztn:ztn%40sim@db:5432/ztn_db
JWT_COOKIE_SECURE=True

# Mail (dev uses Mailpit)
MAIL_SERVER=mailpit
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_DEFAULT_SENDER=dev@example.com
ADMIN_ALERT_EMAIL=dev@example.com
PUBLIC_BASE_URL=https://localhost.localdomain.com

# ZT-Authenticator (enrollment payload routing)
ZT_AUTH_API_BASE_URL=http://192.168.60.2/api/auth
ZT_AUTH_IAM_API_BASE_URL=http://192.168.60.2/api/v1/auth

# Optional: disable WebAuthn in non-HTTPS dev flows
ZT_DISABLE_WEBAUTHN=true
```

## Running with Docker/Podman
```bash
./run.sh
```
To rebuild images:
```bash
./run.sh --build
```

App endpoints:
- Home: `https://localhost.localdomain.com/`
- API docs: `https://localhost.localdomain.com/docs`
- Mailpit UI (dev inbox): `http://localhost:8025`

## Database Seeding (dev)
```bash
podman exec -w /app -e PYTHONPATH=/app ztn_momo_app python scripts/seed_data.py
```

## Local Development (without containers)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

## ZT-IAM Research Scripts
Use these when running experiments against the `/api/auth` flow.

```bash
python scripts/collect_iam_metrics.py \
  --base-url https://localhost.localdomain.com \
  --identifier admin@example.com \
  --password 'ChangeMe123!' \
  --insecure
```

```bash
python scripts/collect_iam_frr_sweep.py \
  --base-url https://localhost.localdomain.com \
  --identifier admin@example.com \
  --password 'ChangeMe123!' \
  --insecure
```

Analysis:
```bash
python scripts/analyze_iam_metrics.py
```

## Security Notes
- **Do not commit secrets** or TLS private keys.
- Use strong values for `JWT_SECRET_KEY` and `FLASK_SECRET_KEY`.
- Set `JWT_COOKIE_SECURE=True` in production.

## License
See [`LICENSE`](LICENSE).
