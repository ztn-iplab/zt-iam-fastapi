# utils/email_alerts.py
from flask import url_for
from flask_mail import Message
from flask import current_app
from extensions import mail
from datetime import datetime

def send_alert_email(subject, body):
    try:
        msg = Message(
            subject=subject,
            recipients=[current_app.config['ADMIN_ALERT_EMAIL']],
            body=body
        )
        mail.send(msg)
        print(f"📧 Alert email sent: {subject}")
    except Exception as e:
        print(f"❌ Failed to send alert email: {e}")

def send_admin_alert(user, event_type, ip_address, location, device_info):
    subject = f"🚨 Security Alert: {event_type}"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    body = f"""
Admin,

Suspicious activity detected:

User: {user.first_name} {user.last_name} ({user.email})
Event: {event_type}
Time: {timestamp}
IP Address: {ip_address}
Location: {location}
Device: {device_info}

Take action if necessary.

Regards,
Security Team
"""
    send_alert_email(subject, body)

def send_user_alert(user, event_type, ip_address, location, device_info):
    try:
        subject = f"🚨 Security Alert: {event_type}"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        body = f"""
Dear {user.first_name},

We've detected {event_type.lower()} to your account as of {timestamp}.

IP Address: {ip_address}
Location: {location}
Device: {device_info}

If this wasn't you, please reset your password and contact support immediately.

Regards,
Security Team
"""
        msg = Message(
            subject=subject,
            recipients=[user.email],
            body=body
        )
        mail.send(msg)
        print(f"📧 User alert email sent: {subject}")
    except Exception as e:
        print(f"❌ Failed to send user alert email: {e}")
        
def send_password_reset_email(user, raw_token):
    try:
        reset_link = url_for('auth.reset_password', token=raw_token, _external=True)

        subject = "🔐 Reset Your Password"
        body = f"""
Dear {user.first_name},

We received a request to reset your MoMo ZTN password.

Click the link below to reset it (valid for 15 minutes):
{reset_link}

If you didn’t request this, you can ignore this email.

Stay secure,  
MoMo ZTN Security Team
"""

        msg = Message(
            subject=subject,
            recipients=[user.email],
            body=body
        )
        mail.send(msg)
        print(f"📧 Password reset email sent to {user.email}")

    except Exception as e:
        print(f"❌ Failed to send password reset email: {e}")
        
def send_totp_reset_email(user, raw_token):
    try:
        reset_link = url_for('auth.verify_totp_reset', token=raw_token, _external=True)
        subject = "🔁 Reset Your TOTP (Authenticator App)"
        body = f"""
Dear {user.first_name},

We received a request to reset your TOTP (Authenticator App) setup for your MoMo ZTN account.

Click the link below to verify your identity and reset your TOTP:
{reset_link}

This link will expire in 15 minutes.

If you did not request this reset, please secure your account and contact support immediately.

Regards,  
MoMo ZTN Security Team
"""
        msg = Message(
            subject=subject,
            recipients=[user.email],
            body=body
        )
        mail.send(msg)
        print(f"📧 TOTP reset email sent to {user.email}")
    except Exception as e:
        print(f"❌ Failed to send TOTP reset email: {e}")

def send_webauthn_reset_email(user, raw_token):
    try:
        reset_link = url_for('auth.verify_webauthn_reset', token=raw_token, _external=True)
        subject = "🗝️ Reset Your WebAuthn Passkey"
        body = f"""
Dear {user.first_name},

We received a request to reset your WebAuthn (passkey) setup for your MoMo ZTN account.

Click the link below to verify your identity and reset your passkey:
{reset_link}

This link will expire in 15 minutes.

If you did not request this, please reset your password and contact support immediately.

Stay secure,  
MoMo ZTN Security Team
"""
        msg = Message(subject=subject, recipients=[user.email], body=body)
        mail.send(msg)
        print(f"📧 WebAuthn reset email sent to {user.email}")
    except Exception as e:
        print(f"❌ Failed to send WebAuthn reset email: {e}")



def send_sim_swap_verification_email(user, raw_token):
    try:
        reset_link = url_for('auth.verify_sim_swap', token=raw_token, _external=True)
        subject = "🔐 SIM Swap Verification Required"
        body = f"""
Dear {user.first_name},

A request was made to swap the SIM card linked to your account.

To proceed, please verify your identity by clicking the link below:
{reset_link}

This link will expire in 15 minutes. If you did not initiate this, please reset your password immediately and report the incident.

Stay secure,  
MoMo ZTN Security Team
"""
        msg = Message(subject=subject, recipients=[user.email], body=body)
        mail.send(msg)
        print(f"📧 SIM swap verification email sent to {user.email}")
    except Exception as e:
        print(f"❌ Failed to send SIM swap email: {e}")
