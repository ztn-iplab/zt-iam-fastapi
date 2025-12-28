from app.email import send_email


def send_tenant_password_reset_email(user, raw_token, tenant_name, tenant_email, reset_link):
    subject = f"Reset Your Password - {tenant_name}"
    body = f"""
Dear {user.first_name},

We received a request to reset your password for your {tenant_name} account.

Click the link below to reset it (valid for 15 minutes):
{reset_link}

If you didn’t request this, you can ignore this email.

Stay secure,
{tenant_name} Security Team
"""
    send_email(subject, body, [tenant_email])


def send_tenant_totp_reset_email(user, raw_token, tenant_name, tenant_email, reset_link):
    subject = f"TOTP Reset Request - {tenant_name}"
    body = f"""
Dear {user.first_name},

We received a request to reset your Two-Factor Authentication (TOTP) for your {tenant_name} account.

Click the link below to proceed with verification and reset your TOTP setup (valid for 15 minutes):
{reset_link}

If you did not request this reset or still have access to your authenticator app, you can ignore this email.

For your security, always keep your MFA device safe.

Best regards,
{tenant_name} Security Team
"""
    send_email(subject, body, [tenant_email])


def send_tenant_webauthn_reset_email(user, raw_token, tenant_name, tenant_email, reset_link):
    subject = f"WebAuthn Reset Request - {tenant_name}"
    body = f"""
Dear {user.first_name},

We received a request to reset your WebAuthn for your {tenant_name} account.

Click the link below to proceed with verification and reset your WebAuthn setup (valid for 15 minutes):
{reset_link}

If you did not request this reset or still have access to your authenticator app, you can ignore this email.

For your security, always keep your MFA device safe.

Best regards,
{tenant_name} Security Team
"""
    send_email(subject, body, [tenant_email])
