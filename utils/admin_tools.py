from models.models import (
    db, Tenant, TenantUser, UserAccessControl, UserAuthLog, RealTimeLog,
    TenantPasswordHistory, TenantTrustPolicyFile, WebAuthnCredential
)
from sqlalchemy import delete
from sqlalchemy.orm import load_only

def delete_tenant_cascade(tenant_id, logger=None):
    try:
        # Step 1: Get tenant (for logging/debugging if needed)
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return {"error": "Tenant not found"}, 404

        # if logger:
        #     logger.info(f"🔁 Starting deletion for tenant {tenant.name} (ID: {tenant.id})")

        # Step 2: Fetch all tenant user IDs (for joined deletes)
        tenant_user_ids = [
            t.id for t in TenantUser.query
            .filter_by(tenant_id=tenant_id)
            .options(load_only(TenantUser.id))
            .all()
        ]

        # Step 3: Delete related records in safe order
        TenantPasswordHistory.query.filter(TenantPasswordHistory.tenant_user_id.in_(tenant_user_ids)).delete(synchronize_session=False)
        UserAccessControl.query.filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        WebAuthnCredential.query.filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        TenantTrustPolicyFile.query.filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        UserAuthLog.query.filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        RealTimeLog.query.filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        TenantUser.query.filter_by(tenant_id=tenant_id).delete(synchronize_session=False)

        # Step 4: Delete the actual tenant
        db.session.delete(tenant)
        db.session.commit()

        # if logger:
        #     logger.info(f"✅ Successfully deleted tenant {tenant.name} and all related data.")

        return {"message": f"Tenant '{tenant.name}' deleted successfully"}, 200

    except Exception as e:
        db.session.rollback()
        if logger:
            logger.error(f"❌ Error deleting tenant ID {tenant_id}: {e}")
        return {"error": "Failed to delete tenant due to internal error"}, 500
