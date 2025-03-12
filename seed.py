import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from main import app, db
from models.models import User, UserRole, UserAccessControl, SIMCard, Wallet, Transaction
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# ✅ Sample user data for testing
users_data = [
    {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "country": "Rwanda", "password": "password123"},
    {"first_name": "Jane", "last_name": "Smith", "email": "jane.smith@example.com", "country": "Kenya", "password": "password123"},
    {"first_name": "Kwame", "last_name": "Nkrumah", "email": "kwame.nkrumah@example.com", "country": "Ghana", "password": "password123"},
]

# ✅ Generate random ICCID and Mobile Numbers
def generate_unique_mobile_number():
    while True:
        new_number = "0787" + str(random.randint(100000, 999999))  # Example Rwandan format
        existing_number = SIMCard.query.filter_by(mobile_number=new_number).first()
        if not existing_number:
            return new_number

def generate_unique_iccid():
    while True:
        new_iccid = "8901" + str(random.randint(100000000000, 999999999999))
        existing_iccid = SIMCard.query.filter_by(iccid=new_iccid).first()
        if not existing_iccid:
            return new_iccid

# ✅ Seed Data Function
def seed_data():
    with app.app_context():
        print("🌱 Seeding the database...")

        # Insert users
        users = []
        for data in users_data:
            password_hash = generate_password_hash(data["password"])  # Hash password
            user = User(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                country=data["country"],
                password_hash=password_hash,
                identity_verified=True,
                trust_score=round(random.uniform(0.5, 1.0), 2),  
                last_login=datetime.utcnow() - timedelta(days=random.randint(1, 30)), 
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()  # ✅ Flush to get user.id before committing

            # ✅ Assign a SIM card with a mobile number
            sim = SIMCard(
                iccid=generate_unique_iccid(),
                mobile_number=generate_unique_mobile_number(),
                network_provider="MTN Rwanda",
                status="active",
                registered_by="Admin",
                user_id=user.id  # Link SIM to User
            )
            db.session.add(sim)

            users.append(user)

        db.session.commit()  # ✅ Save users & SIMs

        # ✅ Insert Wallets
        wallets = []
        for user in users:
            wallet = Wallet(
                user_id=user.id,
                balance=round(random.uniform(10, 5000), 2), 
                currency="RWF",
                last_transaction_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
            )
            db.session.add(wallet)
            wallets.append(wallet)

        db.session.commit()  # ✅ Save wallets

        # ✅ Insert Transactions for Users
        for user in users:
            for _ in range(3):  
                transaction = Transaction(
                    user_id=user.id,
                    amount=round(random.uniform(5, 2000), 2),
                    transaction_type=random.choice(["deposit", "withdrawal", "transfer"]),
                    status=random.choice(["pending", "completed", "failed"]),
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
                    location=random.choice(["Kigali, Rwanda", "Nairobi, Kenya", "Accra, Ghana"]),
                    device_info=random.choice(["iPhone 13, iOS 16", "Samsung S21, Android 12"]),
                    fraud_flag=random.choice([True, False]),
                    risk_score=round(random.uniform(0, 1), 2),
                    transaction_metadata="{'source': 'mobile_app', 'method': 'card_payment'}"
                )
                db.session.add(transaction)

        db.session.commit()  # ✅ Save transactions

        print("✅ Seeding complete!")

# ✅ Run the seeding script
if __name__ == "__main__":
    seed_data()

