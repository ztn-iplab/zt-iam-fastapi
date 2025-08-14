# ZTN_SIM

ZTN_SIM is a Flask-based microservice for managing SIM card registration, user identities, and mobile-money operations with a Zero Trust approach. 
The service integrates JWT authentication, role-based access control, and logging, making it suitable for secure environments.

## Features

- **Flask application with modular blueprints** for authentication, wallets, transactions, roles, admin tasks, and WebAuthn endpoints.
- **JWT-based security with access** and refresh tokens stored in cookies for session continuity.
- **Role-based access control (RBAC)** allowing per-tenant user roles and access levels.
- **SIM card management** including registration and swap operations.
- **Wallet and transaction tracking** with fraud detection fields.
- **Email notifications and logging** for audit and alerting.
- **Docker and Docker Compose** support for containerized deployment.

## Project Structure

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
```

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Git
- (Optional) Docker and Docker Compose

### Local Setup

1. Clone the repository and navigate into it:
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
   ```bash
   flask db upgrade
   ```
6. Run the development server:
   ```bash
   python main.py
   ```

### Running with Docker

1. Copy SSL certificates into `certs/` and private keys into `private/`.
2. Build and start the services:
   ```bash
   ./up.sh
   ```
3. The app is exposed behind NGINX on port 443.

To stop the services:
```bash
./stop.sh
```

## Key Configuration

- Database URL and other settings are configured in `config.py`.
- Logging writes to `logs/ztn_momo.log` via utilities under `utils/logger.py`.
- Default Docker image uses Python 3.10 and runs Gunicorn for production.

## License

This project is released under the MIT License. See `LICENSE` for details.
