from datetime import datetime
from models.models import UserAuthLog

def calculate_risk_score(user, amount, location, device_info, ip_address):
    score = 0.0

    # Rule 1: Large transfer
    avg_amount = 10000  # Can improve later with historical data
    if amount > avg_amount * 3:
        score += 0.4

    # Rule 2: Odd hours
    hour = datetime.now().hour
    if hour in [1, 2, 3, 4]:
        score += 0.2

    # Rule 3: New device or IP
    recent_logs = UserAuthLog.query.filter_by(user_id=user.id).order_by(UserAuthLog.auth_timestamp.desc()).limit(5).all()

    if not any(log.device_info == device_info for log in recent_logs):
        score += 0.2

    if not any(log.ip_address == ip_address for log in recent_logs):
        score += 0.2

    # Rule 4: Geo trust score
    if user.trust_score < 0.3:
        score += 0.2

    return round(min(score, 1.0), 2)
