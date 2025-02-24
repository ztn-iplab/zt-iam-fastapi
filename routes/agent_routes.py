from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import role_required
from models.models import db, SIMRegistration

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/agent/verify_sim", methods=["POST"])
@jwt_required()
@role_required(["admin", "agent"])
def verify_sim():
    """Agents or Admins can verify SIM registrations"""
    data = request.get_json()
    sim_record = SIMRegistration.query.get(data.get("sim_id"))
    
    if not sim_record:
        return jsonify({"error": "SIM record not found"}), 404
    
    sim_record.status = "verified"
    db.session.commit()
    
    return jsonify({"message": "SIM verified successfully"}), 200
