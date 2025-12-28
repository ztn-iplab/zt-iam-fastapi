import secrets
from datetime import datetime

from app.db import SessionLocal
from app.models import (
    HeadquartersWallet,
    PasswordHistory,
    SIMCard,
    Tenant,
    User,
    UserAccessControl,
    UserRole,
    Wallet,
)


def get_or_create_tenant(db):
    tenant = db.query(Tenant).filter_by(id=1).first()
    if tenant:
        return tenant

    api_key = secrets.token_hex(24)
    tenant = Tenant(
        id=1,
        name="Master Tenant",
        api_key=api_key,
        contact_email="ops@example.com",
        plan="enterprise",
    )
    db.add(tenant)
    db.commit()
    return tenant


def get_or_create_role(db, tenant_id, role_name):
    role = db.query(UserRole).filter_by(role_name=role_name, tenant_id=tenant_id).first()
    if role:
        return role
    role = UserRole(role_name=role_name, tenant_id=tenant_id)
    db.add(role)
    db.commit()
    return role


def get_or_create_user(db, tenant_id, email, first_name, password):
    user = db.query(User).filter_by(email=email).first()
    if user:
        return user
    user = User(
        email=email,
        first_name=first_name,
        last_name="Seed",
        tenant_id=tenant_id,
        is_active=True,
        identity_verified=True,
    )
    user.password = password
    db.add(user)
    db.commit()
    return user


def ensure_access(db, user_id, tenant_id, role_id, access_level="full"):
    access = db.query(UserAccessControl).filter_by(user_id=user_id, tenant_id=tenant_id).first()
    if access:
        access.role_id = role_id
        access.access_level = access_level
        db.commit()
        return access
    access = UserAccessControl(
        user_id=user_id,
        tenant_id=tenant_id,
        role_id=role_id,
        access_level=access_level,
    )
    db.add(access)
    db.commit()
    return access


def ensure_wallet(db, user_id, balance=0.0):
    wallet = db.query(Wallet).filter_by(user_id=user_id).first()
    if wallet:
        return wallet
    wallet = Wallet(user_id=user_id, balance=balance, currency="RWF")
    db.add(wallet)
    db.commit()
    return wallet


def ensure_password_history(db, user):
    exists = db.query(PasswordHistory).filter_by(user_id=user.id).first()
    if exists or not user.password_hash:
        return exists
    history = PasswordHistory(user_id=user.id, password_hash=user.password_hash)
    db.add(history)
    db.commit()
    return history


def ensure_sim(db, iccid, mobile_number, status, user_id=None, registered_by="seed"):
    sim = db.query(SIMCard).filter_by(iccid=iccid).first()
    if sim:
        return sim
    sim = SIMCard(
        iccid=iccid,
        mobile_number=mobile_number,
        network_provider="MTN Rwanda",
        status=status,
        registered_by=str(registered_by),
        registration_date=datetime.utcnow(),
        user_id=user_id,
    )
    db.add(sim)
    db.commit()
    return sim


def ensure_hq_wallet(db, balance=1000000.0):
    wallet = db.query(HeadquartersWallet).first()
    if wallet:
        return wallet
    wallet = HeadquartersWallet(balance=balance)
    db.add(wallet)
    db.commit()
    return wallet


def main():
    db = SessionLocal()
    try:
        tenant = get_or_create_tenant(db)

        admin_role = get_or_create_role(db, tenant.id, "admin")
        agent_role = get_or_create_role(db, tenant.id, "agent")
        user_role = get_or_create_role(db, tenant.id, "user")

        admin = get_or_create_user(
            db,
            tenant.id,
            email="admin@example.com",
            first_name="Admin",
            password="ChangeMe123!",
        )
        agent = get_or_create_user(
            db,
            tenant.id,
            email="agent@example.com",
            first_name="Agent",
            password="ChangeMe123!",
        )
        user = get_or_create_user(
            db,
            tenant.id,
            email="user@example.com",
            first_name="User",
            password="ChangeMe123!",
        )

        ensure_access(db, admin.id, tenant.id, admin_role.id, access_level="full")
        ensure_access(db, agent.id, tenant.id, agent_role.id, access_level="write")
        ensure_access(db, user.id, tenant.id, user_role.id, access_level="read")
        ensure_wallet(db, admin.id, balance=250000.0)
        ensure_wallet(db, agent.id, balance=100000.0)
        ensure_wallet(db, user.id, balance=50000.0)
        ensure_password_history(db, admin)
        ensure_password_history(db, agent)
        ensure_password_history(db, user)

        ensure_sim(
            db,
            iccid="8901000000000000001",
            mobile_number="0787000001",
            status="active",
            user_id=admin.id,
            registered_by="Admin",
        )
        ensure_sim(
            db,
            iccid="8901000000000000002",
            mobile_number="0787000002",
            status="active",
            user_id=agent.id,
            registered_by="Admin",
        )
        ensure_sim(
            db,
            iccid="8901000000000000003",
            mobile_number="0787000003",
            status="active",
            user_id=user.id,
            registered_by="Admin",
        )

        ensure_sim(
            db,
            iccid="8901000000000001001",
            mobile_number="0787000101",
            status="unregistered",
            user_id=None,
            registered_by="Admin",
        )
        ensure_sim(
            db,
            iccid="8901000000000001002",
            mobile_number="0787000102",
            status="unregistered",
            user_id=None,
            registered_by="Admin",
        )

        ensure_hq_wallet(db)

        print("Seed complete.")
        print("Admin login: admin@example.com / ChangeMe123!")
        print("Agent login: agent@example.com / ChangeMe123!")
        print("User login: user@example.com / ChangeMe123!")
        print("Unregistered ICCID for signup: 8901000000000001001")
        print("User mobile for testing: 0787000003")
    finally:
        db.close()


if __name__ == "__main__":
    main()
