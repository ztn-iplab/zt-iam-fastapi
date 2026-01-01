from models.models import db, UserRole, TenantUser, UserAccessControl
from flask import Flask
from main import app 

#  You can change this if assigning roles to another tenant
tenant_id = 2

#  Mapping of company_email to role name
role_assignments = {
    "pathos2m@gmail.com": "doctor",
    "user@example.com": None,  # No role assigned
    "dary@minheal.com": "nurse",
    "bztniplab@gmail.com": "admin",
}

#  Use app context to access DB
with app.app_context():
    for email, role_name in role_assignments.items():
        tenant_user = TenantUser.query.filter_by(company_email=email, tenant_id=tenant_id).first()

        if not tenant_user:
            print(f"❌ No TenantUser found for {email}")
            continue

        if role_name is None:
            print(f"ℹ️ Skipping role assignment for {email}")
            continue

        role = UserRole.query.filter_by(role_name=role_name, tenant_id=tenant_id).first()
        if not role:
            print(f"❌ Role '{role_name}' not found for tenant ID {tenant_id}")
            continue

        access = UserAccessControl.query.filter_by(user_id=tenant_user.user_id, tenant_id=tenant_id).first()
        if not access:
            access = UserAccessControl(
                user_id=tenant_user.user_id,
                role_id=role.id,
                tenant_id=tenant_id,
                access_level="write"
            )
            db.session.add(access)
            print(f"✅ Added role '{role_name}' for {email}")
        else:
            access.role_id = role.id
            print(f"🔁 Updated role to '{role_name}' for {email}")

    db.session.commit()
    print("✅ All roles assigned successfully.")
