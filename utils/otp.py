import random
from datetime import datetime, timedelta

from app.email import send_email
from app.models import OTPCode


def generate_otp_code(db, user):
    otp_code = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=5)

    otp = OTPCode(user_id=user.id, code=otp_code, expires_at=expiry, tenant_id=1)
    db.add(otp)
    db.commit()

    send_email(
        subject="Your OTP Code",
        body=f"Your OTP code is: {otp_code}. It will expire in 5 minutes.",
        recipients=[user.email],
    )
    return otp_code
