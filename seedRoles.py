# seed_roles.py

from models.models import db, UserRole
from main import app  

with app.app_context():
    # Optional: Clear existing roles if needed
    UserRole.query.delete()
    
    # Define robust permissions for a mobile money system

    # Admin: Full control including deletion, updating, role assignments, and monitoring
    admin_permissions = {
        "can_delete": True,
        "can_update": True,
        "can_assign_roles": True,
        "can_view_all_transactions": True,
        "can_verify_transactions": True,
        "can_suspend_users": True,
        "can_modify_trust_scores": True,
        "can_access_reports": True
    }

    # Agent: Handles transactions and verification at the branch/agent level
    agent_permissions = {
        "can_transact": True,
        "can_verify_transactions": True,
        "can_update": False,
        "can_access_reports": False
    }

    # User: Basic capabilities to transact and update their own profile
    user_permissions = {
        "can_transact": True,
        "can_update": True,
        "can_view_own_transactions": True
    }

    # Create roles
    admin_role = UserRole(role_name="admin", permissions=admin_permissions)
    agent_role = UserRole(role_name="agent", permissions=agent_permissions)
    user_role = UserRole(role_name="user", permissions=user_permissions)

    # Add roles to the database session
    db.session.add(admin_role)
    db.session.add(agent_role)
    db.session.add(user_role)
    db.session.commit()

    print("Roles seeded successfully!")

