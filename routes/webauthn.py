from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity

from fido2.server import Fido2Server
from fido2.utils import websafe_decode, websafe_encode
from fido2.cbor import decode as cbor_decode
from fido2.webauthn import (
    PublicKeyCredentialRpEntity,
    AuthenticatorData
)

from models.models import db, User, WebAuthnCredential
from enum import Enum
from fido2.cose import ES256
from fido2 import cbor


webauthn_bp = Blueprint('webauthn', __name__)

rp = PublicKeyCredentialRpEntity(id="localhost", name="ZTN Local")
server = Fido2Server(rp)


def jsonify_webauthn(data):
    if isinstance(data, dict):
        return {
            k: jsonify_webauthn(v)
            for k, v in data.items()
            if k != "_field_keys"
        }
    elif isinstance(data, list):
        return [jsonify_webauthn(v) for v in data]
    elif isinstance(data, bytes):
        return websafe_encode(data).decode()
    elif isinstance(data, Enum):
        return data.value
    elif hasattr(data, "__dict__"):
        return jsonify_webauthn(vars(data))
    elif isinstance(data, str):
        return data
    return data


@webauthn_bp.route("/webauthn/register-begin", methods=["POST"])
@jwt_required()
def begin_registration():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    credentials = [
        {
            "id": c.credential_id,
            "transports": c.transports.split(',') if c.transports else [],
            "type": "public-key"
        }
        for c in user.webauthn_credentials
    ]

    try:
        registration_data, state = server.register_begin({
            "id": str(user.id).encode(),
            "name": user.email,
            "displayName": f"{user.first_name} {user.last_name}"
        }, credentials)

        session['webauthn_register_state'] = state

        public_key = jsonify_webauthn(registration_data["publicKey"])
        return jsonify({"public_key": public_key})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server failed to prepare biometric registration."}), 500


@webauthn_bp.route("/webauthn/register-complete", methods=["POST"])
@jwt_required()
def complete_registration():
    try:
        data = request.get_json()
        state = session.get("webauthn_register_state")
        if not state:
            return jsonify({"error": "No registration in progress."}), 400

        user = User.query.get(get_jwt_identity())
        if not user:
            return jsonify({"error": "User not found"}), 404

        if data["id"] != data["rawId"]:
            return jsonify({"error": "id does not match rawId"}), 400

        response = {
            "id": data["id"],
            "rawId": data["rawId"],
            "type": data["type"],
            "response": {
                "attestationObject": data["response"]["attestationObject"],
                "clientDataJSON": data["response"]["clientDataJSON"]
            }
        }

        auth_data = server.register_complete(state, response)
        cred_data = auth_data.credential_data

        # ✅ This WILL work — serializes COSEKey using CBOR
        public_key_bytes = cbor.encode(cred_data.public_key)

        credential = WebAuthnCredential(
            user_id=user.id,
            credential_id=cred_data.credential_id,
            public_key=public_key_bytes,
            sign_count=0,
            transports=",".join(data.get("transports", []))
        )

        db.session.add(credential)
        db.session.commit()
        session.pop("webauthn_register_state", None)

        return jsonify({"message": "✅ WebAuthn credential registered."})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"❌ Registration failed: {str(e)}"}), 500





@webauthn_bp.route("/webauthn/assertion-begin", methods=["POST"])
def begin_assertion():
    email = request.json.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    credentials = [
        {
            "id": c.credential_id,
            "transports": c.transports.split(',') if c.transports else [],
            "type": "public-key"
        }
        for c in user.webauthn_credentials
    ]

    assertion_data, state = server.authenticate_begin(credentials)
    session['webauthn_assertion_state'] = state
    session['assertion_user_id'] = user.id
    return jsonify(jsonify_webauthn(assertion_data))


@webauthn_bp.route("/webauthn/assertion-complete", methods=["POST"])
def complete_assertion():
    data = request.get_json()
    state = session.get("webauthn_assertion_state")
    user_id = session.get("assertion_user_id")

    if not state or not user_id:
        return jsonify({"error": "No assertion in progress."}), 400

    try:
        credential_id = websafe_decode(data['credentialId'])
        user = User.query.get(user_id)
        credential = WebAuthnCredential.query.filter_by(
            user_id=user.id,
            credential_id=credential_id
        ).first()

        if not credential:
            return jsonify({"error": "Credential not found."}), 404

        auth_data = AuthenticatorData(websafe_decode(data['authenticatorData']))
        client_data = CollectedClientData(websafe_decode(data['clientDataJSON']))
        signature = websafe_decode(data['signature'])

        server.authenticate_complete(
            state,
            credential.public_key,
            auth_data,
            client_data,
            signature
        )

        credential.sign_count = auth_data.sign_count
        db.session.commit()

        return jsonify({
            "message": "✅ WebAuthn authentication successful.",
            "user_id": user.id
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"WebAuthn assertion failed: {str(e)}"}), 500
