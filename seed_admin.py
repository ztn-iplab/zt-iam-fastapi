from models.models import db, User, UserRole, UserAccessControl
from main import app  # Import your Flask app instance

with app.app_context():
    # Ensure the admin role exists
    admin_role = UserRole.query.filter_by(role_name='admin').first()
    if not admin_role:
        admin_role = UserRole(role_name='admin')
        db.session.add(admin_role)
        db.session.commit()
        print("Admin role created.")

    # Check if admin user exists
    admin_email = "super@ztnsim.com"
    admin_user = User.query.filter_by(email=admin_email).first()

    if not admin_user:
        admin_user = User(
            mobile_number="0788888811",
            email=admin_email,
            first_name="Super",
            last_name="Admin",
            country="Rwanda",
            identity_verified=True,
            is_active=True
        )
        admin_user.password = "test@admin"  # ✅ Use password setter instead of hashing manually
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created.")

    # Assign the admin role to the user
    admin_access = UserAccessControl.query.filter_by(user_id=admin_user.id, role_id=admin_role.id).first()
    if not admin_access:
        admin_access = UserAccessControl(user_id=admin_user.id, role_id=admin_role.id, access_level='admin')
        db.session.add(admin_access)
        db.session.commit()
        print("Admin role assigned.")

print("Admin setup completed successfully!")

