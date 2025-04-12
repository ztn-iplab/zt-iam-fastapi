from flask import Blueprint, request, jsonify, session, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.location import get_ip_location
from fido2.server import Fido2Server
from fido2.utils import websafe_decode, websafe_encode
from fido2.cbor import decode as cbor_decode
from fido2.webauthn import (
    PublicKeyCredentialRpEntity,
    AuthenticatorData,
    AuthenticatorAssertionResponse
)
from models.models import db, User, WebAuthnCredential, UserAccessControl, UserRole, RealTimeLog, UserAuthLog
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
@jwt_required()
def begin_assertion():
    try:
        from fido2.webauthn import PublicKeyCredentialRequestOptions

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.webauthn_credentials:
            return jsonify({"error": "No registered WebAuthn credentials for this user"}), 404

        credentials = [
            {
                "id": c.credential_id,
                "transports": c.transports.split(',') if c.transports else [],
                "type": "public-key"
            }
            for c in user.webauthn_credentials
        ]

        # 👇 Begin authentication
        assertion_data, state = server.authenticate_begin(credentials)

        # 🔐 Store session for completion
        session["webauthn_assertion_state"] = state
        session["assertion_user_id"] = user.id
        session["mfa_webauthn_verified"] = False

        # ✅ Manually serialize clean dict
        options: PublicKeyCredentialRequestOptions = assertion_data.public_key

        public_key_dict = {
            "challenge": websafe_encode(options.challenge),
            "rpId": options.rp_id,
            "allowCredentials": [
                {
                    "type": c.type.value,
                    "id": websafe_encode(c.id),
                    "transports": [t.value for t in c.transports] if c.transports else []
                }
                for c in options.allow_credentials or []
            ],
            "userVerification": options.user_verification,
            "timeout": options.timeout
        }

        return jsonify({"public_key": public_key_dict})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Assertion begin failed: {str(e)}"}), 500


@webauthn_bp.route("/webauthn/assertion-complete", methods=["POST"])
@jwt_required()
def complete_assertion():
    from fido2.utils import websafe_decode
    try:
        data = request.get_json()
        state = session.get("webauthn_assertion_state")
        user_id = session.get("assertion_user_id")

        if not state or not user_id:
            return jsonify({"error": "No assertion in progress."}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        credential_id = websafe_decode(data["credentialId"])
        credential = WebAuthnCredential.query.filter_by(
            user_id=user.id,
            credential_id=credential_id
        ).first()

        if not credential:
            return jsonify({"error": "Credential not found."}), 404

        # ✅ Build WebAuthn response object (as dict)
            assertion = {
                "id": data["credentialId"],
                "rawId": websafe_decode(data["credentialId"]),
                "type": "public-key",
                "response": {
                    "authenticatorData": websafe_decode(data["authenticatorData"]),
                    "clientDataJSON": websafe_decode(data["clientDataJSON"]),
                    "signature": websafe_decode(data["signature"]),
                    "userHandle": websafe_decode(data["userHandle"]) if data.get("userHandle") else None
                }
            }

            # ✅ Credential from DB
            public_key_source = {
                "id": credential.credential_id,
                "public_key": credential.public_key,
                "sign_count": credential.sign_count,
                "transports": credential.transports.split(",") if credential.transports else [],
                "user_handle": None,
            }

            # ✅ Final auth check (note: NO brackets on `assertion`)
            server.authenticate_complete(
                state,
                assertion,
                [public_key_source]
            )

        # 🎉 Success
        credential.sign_count += 1
        db.session.commit()
        session["mfa_webauthn_verified"] = True
        session.pop("webauthn_assertion_state", None)
        session.pop("assertion_user_id", None)

        access = UserAccessControl.query.filter_by(user_id=user.id).first()
        role = db.session.get(UserRole, access.role_id).role_name.lower() if access else "user"

        urls = {
            "admin": url_for("admin.admin_dashboard", _external=True),
            "agent": url_for("agent.agent_dashboard", _external=True),
            "user": url_for("user.user_dashboard", _external=True)
        }

        # 🧬 Determine login method based on credential metadata
        transports = credential.transports.split(",") if credential.transports else []
        if "hybrid" in transports:
            method = "cross-device passkey"
        elif "usb" in transports:
            method = "USB security key"
        elif "internal" in transports:
            # Heuristic: if on desktop and using internal, likely platform auth (fingerprint or passkey)
            user_agent = request.user_agent.string.lower()
            if "android" in user_agent or "iphone" in user_agent:
                method = "platform authenticator (fingerprint)"
            elif "chrome" in user_agent and "linux" in user_agent:
                method = "passkey via Chrome Sync (Google account)"
            else:
                method = "platform authenticator (fingerprint)"
        else:
            method = "unknown method"


        # 🛡️ RealTimeLog entry for login
        db.session.add(RealTimeLog(
            user_id=user.id,
            action=f"🔐 Logged in via WebAuthn ({method})",
            ip_address=request.remote_addr,
            device_info=request.user_agent.string,
            location=get_ip_location(request.remote_addr),
            risk_alert=False
        ))

        # 🧾 UserAuthLog entry
        db.session.add(UserAuthLog(
            user_id=user.id,
            auth_method="webauthn",
            auth_status="success",
            ip_address=request.remote_addr,
            device_info=request.user_agent.string,
            location=get_ip_location(request.remote_addr),
            failed_attempts=0
        ))

        db.session.commit()
        session.pop("webauthn_register_state", None)

        return jsonify({
            "message": "✅ Biometric/passkey login successful",
            "user_id": user.id,
            "dashboard_url": urls.get(role, url_for("user.user_dashboard", _external=True))
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"❌ Assertion failed: {str(e)}"}), 500



