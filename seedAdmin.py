from models.models import db, User, UserRole, UserAccessControl, SIMCard
from main import app
from werkzeug.security import generate_password_hash
import random

# ✅ Generate unique mobile number for admin
def generate_unique_mobile_number():
    while True:
        new_number = "0788" + str(random.randint(100000, 999999))  # Example format
        existing_number = SIMCard.query.filter_by(mobile_number=new_number).first()
        if not existing_number:
            return new_number

# ✅ Generate unique ICCID for admin
def generate_unique_iccid():
    while True:
        new_iccid = "8901" + str(random.randint(100000000000, 999999999999))
        existing_iccid = SIMCard.query.filter_by(iccid=new_iccid).first()
        if not existing_iccid:
            return new_iccid

with app.app_context():
    print("🌱 Seeding Admin User...")

    # ✅ Ensure the admin role exists
    admin_role = UserRole.query.filter_by(role_name='admin').first()
    if not admin_role:
        admin_role = UserRole(role_name='admin')
        db.session.add(admin_role)
        db.session.commit()
        print("✅ Admin role created.")

    # ✅ Check if the admin user exists
    admin_email = "super@ztnsim.com"
    admin_user = User.query.filter_by(email=admin_email).first()

    if not admin_user:
        admin_user = User(
            email=admin_email,
            first_name="Super",
            last_name="Admin",
            country="Rwanda",
            identity_verified=True,
            is_active=True,
            password_hash=generate_password_hash("test@admin")  # ✅ Secure hashing
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created.")

    # ✅ Generate and assign a SIM card to the Admin
    existing_sim = SIMCard.query.filter_by(user_id=admin_user.id).first()

    if not existing_sim:
        admin_sim = SIMCard(
            iccid=generate_unique_iccid(),
            mobile_number=generate_unique_mobile_number(),
            network_provider="MTN Rwanda",
            status="active",
            registered_by="System",
            user_id=admin_user.id
        )
        db.session.add(admin_sim)
        db.session.commit()
        print(f"✅ Admin SIM card created: {admin_sim.mobile_number} | ICCID: {admin_sim.iccid}")

    # ✅ Assign the admin role to the user
    admin_access = UserAccessControl.query.filter_by(user_id=admin_user.id, role_id=admin_role.id).first()
    if not admin_access:
        admin_access = UserAccessControl(user_id=admin_user.id, role_id=admin_role.id, access_level='admin')
        db.session.add(admin_access)
        db.session.commit()
        print("✅ Admin role assigned.")

print("🎯 Admin setup completed successfully!")

