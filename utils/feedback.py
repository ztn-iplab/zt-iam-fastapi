import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.email import send_email

FEEDBACK_EMAIL = os.getenv("FEEDBACK_EMAIL", "")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

def store_feedback(
    payload: Dict[str, Any],
    *,
    source: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    feedback_dir = os.getenv("FEEDBACK_DIR", "feedback")
    os.makedirs(feedback_dir, exist_ok=True)
    path = os.path.join(feedback_dir, "zt_authenticator_feedback.jsonl")

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "email": payload.get("email", ""),
        "category": payload.get("category", ""),
        "subject": payload.get("subject", ""),
        "message": payload.get("message", ""),
    }

    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")

    if FEEDBACK_EMAIL:
        subject = f"Feedback received ({record['source']})"
        body = (
            "New feedback received:\n\n"
            f"Time: {record['timestamp']}\n"
            f"Source: {record['source']}\n"
            f"Email: {record['email']}\n"
            f"Category: {record['category']}\n"
            f"Subject: {record['subject']}\n"
            f"Message: {record['message']}\n"
            f"IP: {record['ip_address']}\n"
            f"User-Agent: {record['user_agent']}\n"
        )
        send_email(subject, body, [FEEDBACK_EMAIL], sender=MAIL_DEFAULT_SENDER)


def load_feedback(limit: int = 200) -> List[Dict[str, Any]]:
    feedback_dir = os.getenv("FEEDBACK_DIR", "feedback")
    path = os.path.join(feedback_dir, "zt_authenticator_feedback.jsonl")
    if not os.path.exists(path):
        return []

    records: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return list(reversed(records[-limit:]))
