import random
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app
from models.models import db, OTPCode
from extensions import mail
import threading

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def generate_otp_code(user):
    otp_code = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=5)

    otp = OTPCode(user_id=user.id, code=otp_code, expires_at=expiry)
    db.session.add(otp)
    db.session.commit()

    # Create the message
    msg = Message(
        subject='Your OTP Code',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        body=f'Your OTP code is: {otp_code}. It will expire in 5 minutes.'
    )

    # Send it asynchronously
    threading.Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
