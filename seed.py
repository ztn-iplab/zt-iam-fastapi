from main import app, db
from models.models import User, Wallet, Transaction
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

# Sample users
users_data = [
    {"mobile_number": "250788111111", "full_name": "John Doe", "country": "Rwanda", "password": "password123"},
    {"mobile_number": "254722222222", "full_name": "Jane Smith", "country": "Kenya", "password": "password123"},
    {"mobile_number": "233244333333", "full_name": "Kwame Nkrumah", "country": "Ghana", "password": "password123"},
]

# Sample transaction details
transaction_types = ["deposit", "withdrawal", "transfer"]
status_choices = ["pending", "completed", "failed"]
locations = ["Kigali, Rwanda", "Nairobi, Kenya", "Accra, Ghana"]
devices = ["iPhone 13, iOS 16", "Samsung S21, Android 12", "MacBook Pro M2, macOS Ventura"]


def seed_data():
    with app.app_context():
        print("🌱 Seeding the database...")

        # Insert users
        users = []
        for data in users_data:
            password_hash = generate_password_hash(data["password"])  # Generate password hash
            user = User(
                mobile_number=data["mobile_number"],
                full_name=data["full_name"],
                country=data["country"],
                password_hash=password_hash,  # Set password hash
                identity_verified=True,  # Assume all users are verified
                trust_score=round(random.uniform(0.5, 1.0), 2),  # Random trust score
                last_login=datetime.utcnow() - timedelta(days=random.randint(1, 30)),  # Random last login
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()  # Save users

        # Insert wallets
        wallets = []
        for user in users:
            wallet = Wallet(
                user_id=user.id,
                balance=round(random.uniform(10, 5000), 2),  # Random balance
                currency="RWF",
                last_transaction_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
            )
            db.session.add(wallet)
            wallets.append(wallet)

        db.session.commit()  # Save wallets

        # Insert transactions
        for user in users:
            for _ in range(3):  # Create 3 random transactions per user
                transaction = Transaction(
                    user_id=user.id,
                    amount=round(random.uniform(5, 2000), 2),
                    transaction_type=random.choice(transaction_types),
                    status=random.choice(status_choices),
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
                    location=random.choice(locations),
                    device_info=random.choice(devices),
                    fraud_flag=random.choice([True, False]),
                    risk_score=round(random.uniform(0, 1), 2),  # Random fraud risk
                    transaction_metadata="{'source': 'mobile_app', 'method': 'card_payment'}"
                )
                db.session.add(transaction)

        db.session.commit()  # Save transactions

        print("✅ Seeding complete!")

if __name__ == "__main__":
    seed_data()

