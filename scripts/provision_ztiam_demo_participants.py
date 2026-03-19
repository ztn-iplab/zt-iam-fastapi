#!/usr/bin/env python3
"""Provision realistic demo participants for HMS/AIg manual studies.

Creates/updates user1@ztiam.demo ... userN@ztiam.demo with:
- valid-format MSISDNs (10 digits, 078/073 prefixes)
- valid-format ICCIDs (20 digits)
- active SIMs linked to users
- tenant user profiles + IAM roles for HMS ("admin", "doctor", "nurse")

Outputs a local CSV registry for experiment coordination.
"""

from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path

from werkzeug.security import generate_password_hash

from app.db import SessionLocal
from app.models import SIMCard, Tenant, TelecomEvent, TenantUser, User, UserAccessControl, UserRole


DEFAULT_PASSWORD = "ZtIamDemo!2026"


@dataclass
class ParticipantRow:
    idx: int
    email: str
    role: str
    provider: str
    mobile_number: str
    iccid: str
    user_id: int
    tenant_user_id: int


@dataclass
class LoginSheetRow:
    idx: int
    email: str
    mobile_number: str
    password: str


def _generate_mobile(existing: set[str], provider: str) -> str:
    prefix = "078" if provider == "MTN" else "073"
    while True:
        value = prefix + str(random.randint(1_000_000, 9_999_999))
        if value not in existing:
            existing.add(value)
            return value


def _generate_iccid(existing: set[str]) -> str:
    while True:
        # 20-digit numeric ICCID-style value.
        value = "89" + str(random.randint(10**17, (10**18) - 1))
        if value not in existing:
            existing.add(value)
            return value


def _role_for_index(idx: int, roles: list[str]) -> str:
    return roles[(idx - 1) % len(roles)]


def _provider_for_index(idx: int) -> str:
    return "MTN" if idx % 2 else "Airtel"


def _provider_for_mobile(mobile_number: str) -> str:
    if mobile_number.startswith("078"):
        return "MTN"
    if mobile_number.startswith("073"):
        return "Airtel"
    return "MTN"


def _load_login_sheet(path: Path) -> list[LoginSheetRow]:
    rows: list[LoginSheetRow] = []
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required = {"participant_no", "email", "mobile_number", "password"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"login sheet missing required columns: {', '.join(sorted(missing))}")
        for raw in reader:
            idx = int(str(raw["participant_no"]).strip())
            email = str(raw["email"]).strip().lower()
            mobile = str(raw["mobile_number"]).strip()
            password = str(raw["password"]).strip()
            if not email or not mobile or not password:
                raise SystemExit(f"Invalid row in login sheet for participant_no={idx}")
            if not (mobile.isdigit() and len(mobile) == 10 and (mobile.startswith("078") or mobile.startswith("073"))):
                raise SystemExit(f"Invalid mobile_number for participant_no={idx}: {mobile}")
            rows.append(
                LoginSheetRow(
                    idx=idx,
                    email=email,
                    mobile_number=mobile,
                    password=password,
                )
            )
    rows.sort(key=lambda r: r.idx)
    return rows


def _ensure_role(db, tenant_id: int, role_name: str) -> UserRole:
    role = db.query(UserRole).filter_by(tenant_id=tenant_id, role_name=role_name).first()
    if role:
        return role
    role = UserRole(role_name=role_name, tenant_id=tenant_id, permissions={})
    db.add(role)
    db.flush()
    return role


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision user1..userN@ztiam.demo participants")
    parser.add_argument("--tenant-id", type=int, default=1)
    parser.add_argument("--count", type=int, default=45)
    parser.add_argument("--email-domain", default="ztiam.demo")
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument(
        "--roles",
        default="admin,agent,user",
        help="Comma-separated IAM roles to cycle (must exist in tenant)",
    )
    parser.add_argument(
        "--output-csv",
        default="experiments/participants/ztiam_demo_participants.csv",
        help="Local registry export path (repo-relative or absolute)",
    )
    parser.add_argument("--seed", type=int, default=20260225)
    parser.add_argument(
        "--login-sheet",
        default="experiments/participants/ztiam_demo_login_sheet.csv",
        help="Optional CSV with participant_no,email,mobile_number,password. If absent, credentials are generated locally.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing participant accounts for the target email domain before seeding.",
    )
    parser.add_argument(
        "--force-password",
        action="store_true",
        help="Always reset user and tenant credentials to --password for seeded participants.",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    roles = [r.strip().lower() for r in args.roles.split(",") if r.strip()]
    if not roles:
        raise SystemExit("At least one role is required")
    allowed_roles = {"admin", "agent", "user"}
    invalid_roles = sorted(set(roles) - allowed_roles)
    if invalid_roles:
        raise SystemExit(
            "Unsupported roles for ZT-IAM participant provisioning: "
            + ", ".join(invalid_roles)
            + ". Allowed: admin, agent, user."
        )

    db = SessionLocal()
    try:
        login_rows: list[LoginSheetRow] = []
        login_sheet_path = Path(args.login_sheet)
        if not login_sheet_path.is_absolute():
            login_sheet_path = Path(__file__).resolve().parents[1] / login_sheet_path
        if login_sheet_path.exists():
            login_rows = _load_login_sheet(login_sheet_path)
            if len(login_rows) < args.count:
                raise SystemExit(
                    f"login sheet only has {len(login_rows)} participant rows, but --count={args.count} was requested"
                )
            login_rows = login_rows[: args.count]

        tenant = db.query(Tenant).get(args.tenant_id)
        if not tenant:
            raise SystemExit(f"Tenant {args.tenant_id} not found")

        role_map = {name: _ensure_role(db, tenant.id, name) for name in set(roles)}

        if args.reset:
            existing_tenant_users = (
                db.query(TenantUser)
                .filter(TenantUser.tenant_id == tenant.id)
                .filter(TenantUser.company_email.like(f"%@{args.email_domain}"))
                .all()
            )
            reset_user_ids = {tu.user_id for tu in existing_tenant_users}
            if reset_user_ids:
                db.query(UserAccessControl).filter(
                    UserAccessControl.tenant_id == tenant.id,
                    UserAccessControl.user_id.in_(reset_user_ids),
                ).delete(synchronize_session=False)
                db.query(TenantUser).filter(
                    TenantUser.tenant_id == tenant.id,
                    TenantUser.user_id.in_(reset_user_ids),
                ).delete(synchronize_session=False)
                db.query(TelecomEvent).filter(
                    TelecomEvent.tenant_id == tenant.id,
                    TelecomEvent.user_id.in_(reset_user_ids),
                ).delete(synchronize_session=False)
                db.query(SIMCard).filter(SIMCard.user_id.in_(reset_user_ids)).delete(synchronize_session=False)
                db.query(User).filter(User.id.in_(reset_user_ids)).delete(synchronize_session=False)
                db.flush()

        existing_mobiles = {m for (m,) in db.query(SIMCard.mobile_number).filter(SIMCard.mobile_number.isnot(None)).all()}
        existing_iccids = {i for (i,) in db.query(SIMCard.iccid).filter(SIMCard.iccid.isnot(None)).all()}

        rows: list[ParticipantRow] = []
        source_rows = list(login_rows)
        if not source_rows:
            source_rows = [
                LoginSheetRow(
                    idx=idx,
                    email=f"user{idx}@{args.email_domain}",
                    mobile_number=_generate_mobile(existing_mobiles, _provider_for_index(idx)),
                    password=args.password,
                )
                for idx in range(1, args.count + 1)
            ]
        for item in source_rows:
            idx = item.idx
            email = item.email
            if not email.endswith(f"@{args.email_domain}"):
                continue
            participant_password = item.password or args.password
            mobile_from_sheet = item.mobile_number
            first_name = f"User{idx}"
            last_name = "Demo"
            role_name = _role_for_index(idx, roles)
            provider = _provider_for_mobile(mobile_from_sheet)

            tenant_user = db.query(TenantUser).filter_by(tenant_id=tenant.id, company_email=email).first()
            user = tenant_user.user if tenant_user else None

            if not user:
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    tenant_id=tenant.id,
                    is_active=True,
                    preferred_mfa="both",
                )
                user.password = participant_password
                db.add(user)
                db.flush()

            # Ensure core user fields are aligned.
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.tenant_id = tenant.id
            user.is_active = True
            if args.force_password or not user.password_hash:
                user.password = participant_password

            sim = db.query(SIMCard).filter_by(user_id=user.id).order_by(SIMCard.id.asc()).first()
            if not sim:
                sim = SIMCard(
                    user_id=user.id,
                    iccid=_generate_iccid(existing_iccids),
                    mobile_number=mobile_from_sheet,
                    network_provider=provider,
                    status="active",
                    registered_by="system_provisioner",
                )
                db.add(sim)
                db.flush()
            else:
                sim.status = "active"
                sim.network_provider = provider if provider in {"MTN", "Airtel"} else sim.network_provider
                sim.mobile_number = mobile_from_sheet
                if not (sim.iccid and sim.iccid.isdigit() and 19 <= len(sim.iccid) <= 20):
                    sim.iccid = _generate_iccid(existing_iccids)

            if not tenant_user:
                tenant_user = TenantUser(
                    tenant_id=tenant.id,
                    user_id=user.id,
                    company_email=email,
                    password_hash=generate_password_hash(participant_password),
                    preferred_mfa="both",
                )
                db.add(tenant_user)
                db.flush()
            else:
                tenant_user.user_id = user.id
                tenant_user.company_email = email
                if args.force_password or not tenant_user.password_hash:
                    tenant_user.password_hash = generate_password_hash(participant_password)
                if not tenant_user.preferred_mfa:
                    tenant_user.preferred_mfa = "both"

            uac = db.query(UserAccessControl).filter_by(user_id=user.id, tenant_id=tenant.id).first()
            if not uac:
                uac = UserAccessControl(
                    user_id=user.id,
                    tenant_id=tenant.id,
                    role_id=role_map[role_name].id,
                    access_level="read",
                )
                db.add(uac)
            else:
                uac.role_id = role_map[role_name].id

            rows.append(
                ParticipantRow(
                    idx=idx,
                    email=email,
                    role=role_name,
                    provider=provider,
                    mobile_number=sim.mobile_number,
                    iccid=sim.iccid,
                    user_id=user.id,
                    tenant_user_id=tenant_user.id,
                )
            )

        db.commit()

        out_path = Path(args.output_csv)
        if not out_path.is_absolute():
            out_path = Path(__file__).resolve().parents[1] / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                ["participant_no", "email", "role", "network_provider", "mobile_number", "iccid", "user_id", "tenant_user_id"]
            )
            for r in rows:
                writer.writerow([r.idx, r.email, r.role, r.provider, r.mobile_number, r.iccid, r.user_id, r.tenant_user_id])

        print(f"Provisioned/updated {len(rows)} participants for tenant_id={tenant.id}")
        print(f"Default password: {args.password}")
        print(f"Wrote registry: {out_path}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
