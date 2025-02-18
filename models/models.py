from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .import db
from werkzeug.security import generate_password_hash


#db = SQLAlchemy()

# 📌 User Model (Identity Management)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    mobile_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=True)#Some people have one name
    identity_verified = db.Column(db.Boolean, default=False)
    country = db.Column(db.String(50))
    trust_score = db.Column(db.Float, default=0.5)  # Score between 0 (low) and 1 (high)
    last_login = db.Column(db.DateTime, nullable=True, default=db.func.current_timestamp())
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    password_hash = db.Column(db.String(255), nullable=False)

    # New field for soft delete
    is_active = db.Column(db.Boolean, default=True)

# Relationships
    auth_logs = db.relationship('UserAuthLog', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    sim_cards = db.relationship('SIMRegistration', backref='user', lazy=True)
    wallet = db.relationship('Wallet', backref='user', uselist=False)  # One-to-One

# password setter and getter
    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 📌 Wallet Model (User Balance & Transactions)
class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default="RWF")
    last_transaction_at = db.Column(db.DateTime, nullable=True)

# 📌 Authentication Logs (Zero Trust Identity Proofing)
class UserAuthLog(db.Model):
    __tablename__ = 'user_auth_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    auth_method = db.Column(db.String(50), nullable=False)  # OTP, biometric, etc.
    auth_status = db.Column(db.String(20))  # success, failed
    auth_timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    ip_address = db.Column(db.String(45))
    location = db.Column(db.String(100))
    device_info = db.Column(db.String(200))
    failed_attempts = db.Column(db.Integer, default=0)  # Failed login tracking
    geo_trust_score = db.Column(db.Float, default=0.5)  # Trust level based on location history

# 📌 Transactions (Mobile Money Operations)
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # deposit, withdrawal, transfer
    status = db.Column(db.String(20))  # pending, completed, failed
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    location = db.Column(db.String(100))
    device_info = db.Column(db.String(200))
    fraud_flag = db.Column(db.Boolean, default=False)
    risk_score = db.Column(db.Float, default=0.0)  # Score for fraud detection
    transaction_metadata = db.Column(db.Text, nullable=True)  # Store JSON-like metadata

# 📌 SIM Card Registration (Ties Users to Mobile Networks)
class SIMRegistration(db.Model):
    __tablename__ = 'sim_registrations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    verified_by = db.Column(db.String(100))  # agent, self-service, etc.
    status = db.Column(db.String(20), default='active')  # active, suspended, expired

# 📌 Role-Based Access Control (RBAC)
class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.Column(db.JSON)  # Store permissions as JSON

class UserAccessControl(db.Model):
    __tablename__ = 'user_access_controls'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'), nullable=False)
    access_level = db.Column(db.String(20), default='read')  # read, write, admin

# 📌 Real-Time Logs (Tracks User Behavior & Security)
class RealTimeLog(db.Model):
    __tablename__ = 'real_time_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Some logs may not be tied to users
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    ip_address = db.Column(db.String(45))
    device_info = db.Column(db.String(200))
    location = db.Column(db.String(100))
    risk_alert = db.Column(db.Boolean, default=False)  # Flagged risky actions
