# utils/email_alerts.py

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
