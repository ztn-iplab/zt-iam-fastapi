from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from datetime import datetime
from .import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import BYTEA 
import base64
from sqlalchemy.schema import UniqueConstraint

#User Model (Identity Management)
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=True)  
    identity_verified = db.Column(db.Boolean, default=False)
    country = db.Column(db.String(50))
    trust_score = db.Column(db.Float, default=0.5)  
    last_login = db.Column(db.DateTime, nullable=True, default=db.func.current_timestamp())
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    password_hash = db.Column(db.String(255), nullable=False)
    otp_secret = db.Column(db.String(32), nullable=True)
    otp_email_label = db.Column(db.String(120), nullable=True)
    reset_token = db.Column(db.String(128), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    preferred_mfa = db.Column(db.String(20), default='both') 

    # Legacy Tenant Association (primary/master tenant)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    is_tenant_admin = db.Column(db.Boolean, default=False)

    #  Account Status
    is_active = db.Column(db.Boolean, default=True)      
    deletion_requested = db.Column(db.Boolean, default=False)
    locked_until = db.Column(db.DateTime, nullable=True)  

    #  Relationships
    access_controls = db.relationship('UserAccessControl', backref='user', lazy=True)
    auth_logs = db.relationship('UserAuthLog', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    sim_cards = db.relationship('SIMCard', backref='user', lazy=True)
    wallet = db.relationship('Wallet', backref='user', uselist=False)

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    #  New method: resolve role by tenant
    def get_role_for_tenant(self, tenant_id):
        from models import UserAccessControl, UserRole  # to avoid circular imports
        access = UserAccessControl.query.filter_by(user_id=self.id, tenant_id=tenant_id).first()
        return UserRole.query.get(access.role_id) if access else None

#  SIM Card Model (Realistic Mobile SIM Registration)
class SIMCard(db.Model):
    __tablename__ = 'sim_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    iccid = db.Column(db.String(20), unique=True, nullable=False)  # Unique SIM Serial Number
    mobile_number = db.Column(db.String(20), unique=True, nullable=False)
    network_provider = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="unregistered")  # active, suspended, lost, swapped
    registered_by = db.Column(db.String(100))  # e.g., "Agent", "User", "Self-service"
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Many-to-One relationship with User (One user can have multiple SIMs)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

#  Sim Swapping operations
class PendingSIMSwap(db.Model):
    __tablename__ = "pending_sim_swap"

    id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(128), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    old_iccid = db.Column(db.String(32), nullable=False)
    new_iccid = db.Column(db.String(32), nullable=False)
    requested_by = db.Column(db.String(64))  # agent_id or email
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)

#Wallet Model (User Balance & Transactions)
class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default="RWF")
    last_transaction_at = db.Column(db.DateTime, nullable=True)

#Authentication Logs (Zero Trust Identity Proofing)
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
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)


#Transactions (Mobile Money Operations)
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # deposit, withdrawal, transfer
    status = db.Column(db.String(20))  # pending, completed, failed
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.Text)
    device_info = db.Column(db.Text)
    fraud_flag = db.Column(db.Boolean, default=False)
    risk_score = db.Column(db.Float, default=0.0)  # Score for fraud detection
    transaction_metadata = db.Column(db.Text, nullable=True)  # Store JSON-like metadata
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)


class PendingTransaction(db.Model):
    __tablename__ = 'pending_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_data = db.Column(db.Text, nullable=False)  # JSON blob
    transaction_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

#Role-Based Access Control (RBAC)
class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)
    permissions = db.Column(db.JSON)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    
    tenant = db.relationship('Tenant', backref='roles')

    __table_args__ = (
        sa.UniqueConstraint('role_name', 'tenant_id', name='uq_role_per_tenant'),
        {'extend_existing': True},  # <<< ✨ THIS IS THE PATCH ✨
    )

class UserAccessControl(db.Model):
    __tablename__ = 'user_access_controls'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'), nullable=False)
    access_level = db.Column(db.String(20), default='read')

    # Relationships
    role = db.relationship('UserRole', backref='user_access_controls')
    tenant = db.relationship('Tenant', backref='user_access_controls')

    # Ensure no duplicate user entries per tenant
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tenant_id', name='uq_user_per_tenant'),
    )



# Real-Time Logs (Tracks User Behavior & Security)
class RealTimeLog(db.Model):
    __tablename__ = 'real_time_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Some logs may not be tied to users
    action = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    ip_address = db.Column(db.String(45))
    device_info = db.Column(db.String(200))
    location = db.Column(db.String(100))
    risk_alert = db.Column(db.Boolean, default=False)  # Flagged risky actions
     # This enables log.user to work
    user = db.relationship("User", backref="real_time_logs")
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)

#One time passowrd for the security purpose
class OTPCode(db.Model):
    __tablename__ = 'otp_codes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref='otp_codes')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)

from sqlalchemy import Numeric

class HeadquartersWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(Numeric(18, 2), default=0.0)  #  Use DECIMAL type


class WebAuthnCredential(db.Model):
    __tablename__ = 'webauthn_credentials'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    credential_id = db.Column(db.LargeBinary, nullable=False)  # ❌ Don't use unique=True here
    public_key = db.Column(db.LargeBinary, nullable=False)
    sign_count = db.Column(db.Integer, default=0)
    transports = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='webauthn_credentials')

    __table_args__ = (
        db.UniqueConstraint("credential_id", "tenant_id", name="uq_credential_per_tenant"),
    )

    def as_dict(self):
        return {
            "type": "public-key",
            "id": base64.urlsafe_b64encode(self.credential_id).decode("utf-8"),
            "transports": self.transports.split(",") if self.transports else []
        }

    def as_webauthn_credential(self):
        from fido2.webauthn import PublicKeyCredentialDescriptor
        return PublicKeyCredentialDescriptor(
            id=self.credential_id,
            type="public-key"
        )
        
class PasswordHistory(db.Model):
    __tablename__ = 'password_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class PendingTOTP(db.Model):
    __tablename__ = 'pending_totps'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    secret = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'tenant_id', name='uq_user_tenant_pending_totp'),
    )

# =====================================
#          For Tenants
# =====================================

class TenantUser(db.Model):
    __tablename__ = 'tenant_users'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # New: Per-tenant TOTP
    otp_secret = db.Column(db.String(64), nullable=True)
    otp_email_label = db.Column(db.String(120), nullable=True)
    preferred_mfa = db.Column(db.String(20), default='both')  # Options: 'totp', 'webauthn', 'both'
     
    tenant = db.relationship('Tenant', backref='tenant_users')
    user = db.relationship('User', backref='tenant_profiles')

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'company_email', name='uq_tenant_user_email'),
    )

class Tenant(db.Model):
    __tablename__ = 'tenants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    plan = db.Column(db.String(50), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    # New: enforce MFA for all users under this tenant/ admin work
    enforce_strict_mfa = db.Column(db.Boolean, default=False)

    # NEW FIELD
    api_key_expires_at = db.Column(db.DateTime, nullable=True)

    # API abuse and tracking
    last_api_access = db.Column(db.DateTime)
    api_request_count = db.Column(db.Integer, default=0)
    api_error_count = db.Column(db.Integer, default=0)
    api_score = db.Column(db.Float, default=0.0)
    api_last_reset = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='tenant', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_score = kwargs.get('api_score', 0.0)
        self.api_request_count = kwargs.get('api_request_count', 0)
        self.api_error_count = kwargs.get('api_error_count', 0)
        self.api_last_reset = kwargs.get('api_last_reset', datetime.utcnow())
        
        # Automatically set expiry based on plan
        if not self.api_key_expires_at:
            if self.plan == 'free':
                self.api_key_expires_at = None  # Free = unlimited
            elif self.plan == 'pro':
                self.api_key_expires_at = datetime.utcnow() + timedelta(days=90)
            elif self.plan == 'enterprise':
                self.api_key_expires_at = datetime.utcnow() + timedelta(days=365)

class TenantPasswordHistory(db.Model):
    __tablename__ = 'tenant_password_history'
    id = db.Column(db.Integer, primary_key=True)
    tenant_user_id = db.Column(db.Integer, db.ForeignKey('tenant_users.id'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    tenant_user = db.relationship('TenantUser', backref='password_history')

class TenantTrustPolicyFile(db.Model):
    __tablename__ = "tenant_trust_policy_file"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), unique=True, nullable=False)
    filename = db.Column(db.String(128))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    config_json = db.Column(db.JSON, nullable=False)

    tenant = db.relationship("Tenant", backref=db.backref("trust_policy_file", uselist=False))
