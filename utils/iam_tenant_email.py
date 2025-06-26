from flask import url_for, current_app
from flask_mail import Message
from extensions import mail
from datetime import datetime


def send_tenant_password_reset_email(user, raw_token, tenant_name, tenant_email, reset_link):
    try:
        subject = f"🔐 Reset Your Password - {tenant_name}"
        body = f"""
Dear {user.first_name},

We received a request to reset your password for your {tenant_name} account.

Click the link below to reset it (valid for 15 minutes):
{reset_link}

If you didn’t request this, you can ignore this email.

Stay secure,  
{tenant_name} Security Team
"""

        msg = Message(
            subject=subject,
            sender=(f"{tenant_name} Security", current_app.config['MAIL_DEFAULT_SENDER']),
            recipients=[tenant_email],
            body=body
        )
        mail.send(msg)
        print(f"📧 Password reset email sent to {tenant_email} from {tenant_name}")

    except Exception as e:
        print(f"❌ Failed to send tenant password reset email: {e}")


def send_tenant_totp_reset_email(user, raw_token, tenant_name, tenant_email, reset_link):
    try:
        subject = f"🔐 TOTP Reset Request - {tenant_name}"
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

        msg = Message(
            subject=subject,
            sender=(f"{tenant_name} Security", current_app.config['MAIL_DEFAULT_SENDER']),
            recipients=[tenant_email],
            body=body
        )
        mail.send(msg)
        print(f"📧 TOTP reset email sent to {tenant_email} from {tenant_name}")

    except Exception as e:
        print(f"❌ Failed to send tenant TOTP reset email: {e}")