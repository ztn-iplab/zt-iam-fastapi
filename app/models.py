import base64
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String(120), unique=True, nullable=False)
    first_name = sa.Column(sa.String(50), nullable=False)
    last_name = sa.Column(sa.String(50), nullable=True)
    identity_verified = sa.Column(sa.Boolean, default=False)
    country = sa.Column(sa.String(50))
    trust_score = sa.Column(sa.Float, default=0.5)
    last_login = sa.Column(sa.DateTime, nullable=True, default=sa.func.current_timestamp())
    created_at = sa.Column(sa.DateTime, default=sa.func.current_timestamp())
    password_hash = sa.Column(sa.String(255), nullable=False)
    otp_secret = sa.Column(sa.String(32), nullable=True)
    otp_email_label = sa.Column(sa.String(120), nullable=True)
    reset_token = sa.Column(sa.String(128), nullable=True)
    reset_token_expiry = sa.Column(sa.DateTime, nullable=True)
    preferred_mfa = sa.Column(sa.String(20), default="both")

    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)
    is_tenant_admin = sa.Column(sa.Boolean, default=False)

    is_active = sa.Column(sa.Boolean, default=True)
    deletion_requested = sa.Column(sa.Boolean, default=False)
    locked_until = sa.Column(sa.DateTime, nullable=True)

    access_controls = relationship("UserAccessControl", backref="user", lazy="select")
    auth_logs = relationship("UserAuthLog", backref="user", lazy="select")
    transactions = relationship("Transaction", backref="user", lazy="select")
    sim_cards = relationship("SIMCard", backref="user", lazy="select")
    wallet = relationship("Wallet", backref="user", uselist=False, lazy="select")

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_role_for_tenant(self, tenant_id):
        access = UserAccessControl.query.filter_by(
            user_id=self.id, tenant_id=tenant_id
        ).first()
        return UserRole.query.get(access.role_id) if access else None


class SIMCard(Base):
    __tablename__ = "sim_cards"

    id = sa.Column(sa.Integer, primary_key=True)
    iccid = sa.Column(sa.String(20), unique=True, nullable=False)
    mobile_number = sa.Column(sa.String(20), unique=True, nullable=False)
    network_provider = sa.Column(sa.String(50), nullable=False)
    status = sa.Column(sa.String(20), default="unregistered")
    registered_by = sa.Column(sa.String(100))
    registration_date = sa.Column(sa.DateTime, default=datetime.utcnow)

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)


class PendingSIMSwap(Base):
    __tablename__ = "pending_sim_swap"

    id = sa.Column(sa.Integer, primary_key=True)
    token_hash = sa.Column(sa.String(128), nullable=False, unique=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    old_iccid = sa.Column(sa.String(32), nullable=False)
    new_iccid = sa.Column(sa.String(32), nullable=False)
    requested_by = sa.Column(sa.String(64))
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    expires_at = sa.Column(sa.DateTime)
    is_verified = sa.Column(sa.Boolean, default=False)


class Wallet(Base):
    __tablename__ = "wallets"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False, unique=True)
    balance = sa.Column(sa.Float, default=0.0)
    currency = sa.Column(sa.String(10), default="RWF")
    last_transaction_at = sa.Column(sa.DateTime, nullable=True)


class UserAuthLog(Base):
    __tablename__ = "user_auth_logs"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    auth_method = sa.Column(sa.String(50), nullable=False)
    auth_status = sa.Column(sa.String(20))
    auth_timestamp = sa.Column(sa.DateTime, default=sa.func.current_timestamp())
    ip_address = sa.Column(sa.String(45))
    location = sa.Column(sa.String(100))
    device_info = sa.Column(sa.String(200))
    failed_attempts = sa.Column(sa.Integer, default=0)
    geo_trust_score = sa.Column(sa.Float, default=0.5)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    transaction_type = sa.Column(sa.String(50), nullable=False)
    status = sa.Column(sa.String(20))
    timestamp = sa.Column(sa.DateTime, default=datetime.utcnow)
    location = sa.Column(sa.Text)
    device_info = sa.Column(sa.Text)
    fraud_flag = sa.Column(sa.Boolean, default=False)
    risk_score = sa.Column(sa.Float, default=0.0)
    transaction_metadata = sa.Column(sa.Text, nullable=True)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)


class PendingTransaction(Base):
    __tablename__ = "pending_transactions"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    transaction_data = sa.Column(sa.Text, nullable=False)
    transaction_type = sa.Column(sa.String(20), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    expires_at = sa.Column(sa.DateTime, nullable=False)
    is_used = sa.Column(sa.Boolean, default=False)


class Device(Base):
    __tablename__ = "devices"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)
    device_label = sa.Column(sa.String(120), nullable=False)
    platform = sa.Column(sa.String(32), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    user = relationship("User", backref="devices")
    tenant = relationship("Tenant", backref="devices")


class DeviceKey(Base):
    __tablename__ = "device_keys"

    id = sa.Column(sa.Integer, primary_key=True)
    device_id = sa.Column(sa.Integer, sa.ForeignKey("devices.id"), nullable=False)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)
    rp_id = sa.Column(sa.String(255), nullable=False)
    key_type = sa.Column(sa.String(32), nullable=False)
    public_key = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    device = relationship("Device", backref="device_keys")
    tenant = relationship("Tenant", backref="device_keys")

    __table_args__ = (
        sa.UniqueConstraint("device_id", "rp_id", "tenant_id", name="uq_device_rp_tenant"),
    )


class LoginChallenge(Base):
    __tablename__ = "login_challenges"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)
    device_id = sa.Column(sa.Integer, sa.ForeignKey("devices.id"), nullable=False)
    rp_id = sa.Column(sa.String(255), nullable=False)
    nonce = sa.Column(sa.String(255), nullable=False)
    otp_hash = sa.Column(sa.String(128), nullable=True)
    status = sa.Column(sa.String(20), default="pending")
    denied_reason = sa.Column(sa.String(100), nullable=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    expires_at = sa.Column(sa.DateTime, nullable=False)
    approved_at = sa.Column(sa.DateTime, nullable=True)

    user = relationship("User", backref="login_challenges")
    device = relationship("Device", backref="login_challenges")
    tenant = relationship("Tenant", backref="login_challenges")


class UserRole(Base):
    __tablename__ = "user_roles"

    id = sa.Column(sa.Integer, primary_key=True)
    role_name = sa.Column(sa.String(50), nullable=False)
    permissions = sa.Column(sa.JSON)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=True)

    tenant = relationship("Tenant", backref="roles")

    __table_args__ = (
        sa.UniqueConstraint("role_name", "tenant_id", name="uq_role_per_tenant"),
        {"extend_existing": True},
    )


class UserAccessControl(Base):
    __tablename__ = "user_access_controls"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)
    role_id = sa.Column(sa.Integer, sa.ForeignKey("user_roles.id"), nullable=False)
    access_level = sa.Column(sa.String(20), default="read")

    role = relationship("UserRole", backref="user_access_controls")
    tenant = relationship("Tenant", backref="user_access_controls")

    __table_args__ = (
        sa.UniqueConstraint("user_id", "tenant_id", name="uq_user_per_tenant"),
    )


class RealTimeLog(Base):
    __tablename__ = "real_time_logs"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    action = sa.Column(sa.String(1000), nullable=False)
    timestamp = sa.Column(sa.DateTime, default=sa.func.current_timestamp())
    ip_address = sa.Column(sa.String(45))
    device_info = sa.Column(sa.String(200))
    location = sa.Column(sa.String(100))
    risk_alert = sa.Column(sa.Boolean, default=False)
    user = relationship("User", backref="real_time_logs")
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    code = sa.Column(sa.String(6), nullable=False)
    is_used = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    expires_at = sa.Column(sa.DateTime, nullable=False)

    user = relationship("User", backref="otp_codes")
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)


class RecoveryCode(Base):
    __tablename__ = "recovery_codes"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)
    code_hash = sa.Column(sa.String(128), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    used_at = sa.Column(sa.DateTime, nullable=True)

    user = relationship("User", backref="recovery_codes")
    tenant = relationship("Tenant", backref="recovery_codes")

    __table_args__ = (
        sa.Index("idx_recovery_code_lookup", "user_id", "tenant_id", "code_hash"),
    )


class HeadquartersWallet(Base):
    __tablename__ = "headquarters_wallet"

    id = sa.Column(sa.Integer, primary_key=True)
    balance = sa.Column(Numeric(18, 2), default=0.0)


class WebAuthnCredential(Base):
    __tablename__ = "webauthn_credentials"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)
    credential_id = sa.Column(sa.LargeBinary, nullable=False)
    public_key = sa.Column(sa.LargeBinary, nullable=False)
    sign_count = sa.Column(sa.Integer, default=0)
    transports = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    user = relationship("User", backref="webauthn_credentials")

    __table_args__ = (
        sa.UniqueConstraint("credential_id", "tenant_id", name="uq_credential_per_tenant"),
    )

    def as_dict(self):
        return {
            "type": "public-key",
            "id": base64.urlsafe_b64encode(self.credential_id).decode("utf-8"),
            "transports": self.transports.split(",") if self.transports else [],
        }

    def as_webauthn_credential(self):
        from fido2.webauthn import PublicKeyCredentialDescriptor
        return PublicKeyCredentialDescriptor(id=self.credential_id, type="public-key")


class PasswordHistory(Base):
    __tablename__ = "password_history"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    password_hash = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime, default=sa.func.now())


class PendingTOTP(Base):
    __tablename__ = "pending_totps"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, nullable=False)
    tenant_id = sa.Column(sa.Integer, nullable=False)
    secret = sa.Column(sa.String(32), nullable=False)
    email = sa.Column(sa.String(255), nullable=False)
    expires_at = sa.Column(sa.DateTime, nullable=False)

    __table_args__ = (
        sa.UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant_pending_totp"),
    )


class TenantUser(Base):
    __tablename__ = "tenant_users"

    id = sa.Column(sa.Integer, primary_key=True)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    company_email = sa.Column(sa.String(120), nullable=False)
    password_hash = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    otp_secret = sa.Column(sa.String(64), nullable=True)
    otp_email_label = sa.Column(sa.String(120), nullable=True)
    preferred_mfa = sa.Column(sa.String(20), default="both")

    tenant = relationship("Tenant", backref="tenant_users")
    user = relationship("User", backref="tenant_profiles")

    __table_args__ = (
        sa.UniqueConstraint("tenant_id", "company_email", name="uq_tenant_user_email"),
    )


class Tenant(Base):
    __tablename__ = "tenants"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False, unique=True)
    api_key = sa.Column(sa.String(64), unique=True, nullable=False)
    contact_email = sa.Column(sa.String(120), nullable=False)
    plan = sa.Column(sa.String(50), default="free")
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    is_active = sa.Column(sa.Boolean, default=True)
    enforce_strict_mfa = sa.Column(sa.Boolean, default=False)

    api_key_expires_at = sa.Column(sa.DateTime, nullable=True)

    last_api_access = sa.Column(sa.DateTime)
    api_request_count = sa.Column(sa.Integer, default=0)
    api_error_count = sa.Column(sa.Integer, default=0)
    api_score = sa.Column(sa.Float, default=0.0)
    api_last_reset = sa.Column(sa.DateTime, default=datetime.utcnow)

    users = relationship("User", backref="tenant", lazy="select")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_score = kwargs.get("api_score", 0.0)
        self.api_request_count = kwargs.get("api_request_count", 0)
        self.api_error_count = kwargs.get("api_error_count", 0)
        self.api_last_reset = kwargs.get("api_last_reset", datetime.utcnow())

        if not self.api_key_expires_at:
            if self.plan == "basic":
                self.api_key_expires_at = None
            elif self.plan == "premium":
                self.api_key_expires_at = datetime.utcnow() + timedelta(days=90)
            elif self.plan == "enterprise":
                self.api_key_expires_at = datetime.utcnow() + timedelta(days=365)


class TenantPasswordHistory(Base):
    __tablename__ = "tenant_password_history"

    id = sa.Column(sa.Integer, primary_key=True)
    tenant_user_id = sa.Column(sa.Integer, sa.ForeignKey("tenant_users.id"), nullable=False)
    password_hash = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime, default=sa.func.now())

    tenant_user = relationship("TenantUser", backref="password_history")


class TenantTrustPolicyFile(Base):
    __tablename__ = "tenant_trust_policy_file"

    id = sa.Column(sa.Integer, primary_key=True)
    tenant_id = sa.Column(sa.Integer, sa.ForeignKey("tenants.id"), unique=True, nullable=False)
    filename = sa.Column(sa.String(128))
    uploaded_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    config_json = sa.Column(sa.JSON, nullable=False)

    tenant = relationship("Tenant", backref=backref("trust_policy_file", uselist=False))
