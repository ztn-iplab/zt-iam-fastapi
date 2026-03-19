#!/usr/bin/env python3
"""Sync IAM users into a tenant and assign doctor/nurse roles for HMS usage.

Defaults:
- target tenant: most recently created non-master tenant
- users: active users with @ztiam.demo emails
- exclusion: users named/email-containing 'murembo'
- split: first half doctors, second half nurses (stable by user id)
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable

from app.db import SessionLocal
from app.models import Tenant, TenantUser, User, UserAccessControl, UserRole


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant-name", default="", help="Target tenant name (defaults to latest non-master tenant)")
    parser.add_argument("--email-domain", default="@ztiam.demo", help="Only include users ending with this domain")
    parser.add_argument("--exclude-token", default="murembo", help="Exclude users where name/email contains this token")
    parser.add_argument("--dry-run", action="store_true", help="Show planned changes without writing")
    return parser.parse_args()


def ensure_role(db, tenant_id: int, role_name: str) -> UserRole:
    role = db.query(UserRole).filter_by(tenant_id=tenant_id, role_name=role_name).first()
    if role:
        return role
    role = UserRole(role_name=role_name, tenant_id=tenant_id)
    db.add(role)
    db.flush()
    return role


def _matches_user_filter(user: User, email_domain: str, exclude_token: str) -> bool:
    email = (user.email or "").strip().lower()
    first = (user.first_name or "").strip().lower()
    last = (user.last_name or "").strip().lower()

    if not email or not email.endswith(email_domain.lower()):
        return False

    token = exclude_token.lower().strip()
    if token and (token in email or token in first or token in last):
        return False

    return True


def split_half(values: list[User]) -> tuple[list[User], list[User]]:
    midpoint = (len(values) + 1) // 2
    return values[:midpoint], values[midpoint:]


def ensure_tenant_user(db, tenant_id: int, user: User) -> TenantUser:
    tenant_user = db.query(TenantUser).filter_by(tenant_id=tenant_id, user_id=user.id).first()
    if tenant_user:
        if not tenant_user.company_email:
            tenant_user.company_email = user.email
        if not tenant_user.password_hash:
            tenant_user.password_hash = user.password_hash
        return tenant_user

    tenant_user = TenantUser(
        tenant_id=tenant_id,
        user_id=user.id,
        company_email=user.email,
        password_hash=user.password_hash,
    )
    db.add(tenant_user)
    return tenant_user


def ensure_access_control(db, tenant_id: int, user_id: int, role_id: int) -> None:
    access = db.query(UserAccessControl).filter_by(user_id=user_id, tenant_id=tenant_id).first()
    if access:
        access.role_id = role_id
        access.access_level = "read"
        return
    db.add(
        UserAccessControl(
            user_id=user_id,
            tenant_id=tenant_id,
            role_id=role_id,
            access_level="read",
        )
    )


def main() -> int:
    args = parse_args()
    db = SessionLocal()
    try:
        if args.tenant_name:
            tenant = db.query(Tenant).filter(Tenant.name == args.tenant_name).first()
        else:
            tenant = (
                db.query(Tenant)
                .filter(Tenant.name != "Master Tenant")
                .order_by(Tenant.created_at.desc(), Tenant.id.desc())
                .first()
            )

        if not tenant:
            raise RuntimeError("No target tenant found")

        users = (
            db.query(User)
            .filter(User.is_active.is_(True))
            .order_by(User.id.asc())
            .all()
        )
        selected = [u for u in users if _matches_user_filter(u, args.email_domain, args.exclude_token)]
        if not selected:
            raise RuntimeError("No users matched the filter; nothing to sync")

        doctor_users, nurse_users = split_half(selected)

        doctor_role = ensure_role(db, tenant.id, "doctor")
        nurse_role = ensure_role(db, tenant.id, "nurse")

        summary: list[str] = []

        for user in doctor_users:
            ensure_tenant_user(db, tenant.id, user)
            ensure_access_control(db, tenant.id, user.id, doctor_role.id)
            summary.append(f"doctor,{user.id},{user.email}")

        for user in nurse_users:
            ensure_tenant_user(db, tenant.id, user)
            ensure_access_control(db, tenant.id, user.id, nurse_role.id)
            summary.append(f"nurse,{user.id},{user.email}")

        if args.dry_run:
            db.rollback()
            print(f"[dry-run] tenant={tenant.id}:{tenant.name}")
        else:
            db.commit()
            print(f"tenant={tenant.id}:{tenant.name}")

        print(f"assigned_total={len(summary)} doctors={len(doctor_users)} nurses={len(nurse_users)}")
        for line in summary:
            print(line)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
