import argparse
import base64
import csv
import json
import os
import ssl
import time
import uuid
from typing import Any, Optional, Tuple
from urllib import error, parse, request

import pyotp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


class IamClient:
    def __init__(self, base_url: str, insecure: bool) -> None:
        self.base_url = base_url.rstrip("/")
        ctx = ssl._create_unverified_context() if insecure else None
        handlers = [request.HTTPCookieProcessor()]
        if ctx:
            handlers.append(request.HTTPSHandler(context=ctx))
        self.opener = request.build_opener(*handlers)

    def request_json(
        self, method: str, path: str, payload: Optional[dict[str, Any]] = None
    ) -> Tuple[int, dict[str, Any]]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method=method,
        )
        try:
            with self.opener.open(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, json.loads(raw) if raw else {}
        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                data = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                data = {"error": raw}
            return exc.code, data

    def post_json(self, path: str, payload: dict[str, Any]) -> Tuple[int, dict[str, Any]]:
        return self.request_json("POST", path, payload)

    def get_json(self, path: str) -> Tuple[int, dict[str, Any]]:
        return self.request_json("GET", path)


def generate_keypair() -> Tuple[ec.EllipticCurvePrivateKey, str]:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_b64 = base64.b64encode(public_bytes).decode("utf-8")
    return private_key, public_b64


def sign_payload(private_key: ec.EllipticCurvePrivateKey, nonce: str, device_id: str, rp_id: str, otp: str) -> str:
    message = f"{nonce}|{device_id}|{rp_id}|{otp}".encode("utf-8")
    signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(signature).decode("utf-8")


def parse_secret(otpauth_uri: str) -> str:
    parsed = parse.urlparse(otpauth_uri)
    query = parse.parse_qs(parsed.query)
    return (query.get("secret") or [""])[0]


def enroll_device(client: IamClient, identifier: str, password: str) -> tuple[str, str, str, str, ec.EllipticCurvePrivateKey]:
    status, _ = client.post_json(
        "/api/auth/login",
        {"identifier": identifier, "password": password},
    )
    if status != 200:
        raise RuntimeError(f"Login failed: status={status}")

    status, setup = client.get_json("/api/auth/setup-totp")
    if status != 200 or "manual_key" not in setup:
        raise RuntimeError(f"Setup TOTP failed: status={status} body={setup}")

    manual_key = setup.get("manual_key") or ""
    if not manual_key:
        raise RuntimeError("No enrollment link returned (manual_key empty).")

    parsed = parse.urlparse(manual_key)
    enroll_path = parsed.path
    if parsed.query:
        enroll_path += f"?{parsed.query}"
    status, payload = client.get_json(enroll_path)
    if status != 200 or payload.get("type") != "zt_totp_enroll":
        raise RuntimeError(f"Enrollment code invalid: status={status} body={payload}")

    private_key, public_b64 = generate_keypair()
    status, enroll_resp = client.post_json(
        "/api/auth/enroll",
        {
            "email": payload["email"],
            "device_label": payload.get("device_label") or "IAM FRR Device",
            "platform": "script",
            "rp_id": payload["rp_id"],
            "rp_display_name": payload.get("rp_display_name") or "ZT-IAM",
            "key_type": "p256",
            "public_key": public_b64,
            "enroll_token": payload["enroll_token"],
        },
    )
    if status != 200:
        raise RuntimeError(f"Enroll failed: status={status} body={enroll_resp}")

    user_id = str(enroll_resp["user"]["id"])
    device_id = str(enroll_resp["device"]["id"])

    status, register = client.post_json(
        "/api/auth/totp/register",
        {
            "user_id": user_id,
            "rp_id": payload["rp_id"],
            "account_name": payload["account_name"],
            "issuer": payload.get("issuer") or "ZT-IAM",
        },
    )
    if status != 200 or "otpauth_uri" not in register:
        raise RuntimeError(f"TOTP register failed: status={status} body={register}")

    secret = parse_secret(register["otpauth_uri"])
    return user_id, device_id, payload["rp_id"], secret, private_key


def totp_verify(client: IamClient, otp: str) -> bool:
    status, _ = client.post_json("/api/auth/verify-totp", {"code": otp})
    return status == 200


def zt_verify(
    client: IamClient,
    user_id: str,
    device_id: str,
    rp_id: str,
    otp: str,
    key: ec.EllipticCurvePrivateKey,
) -> bool:
    status, verify = client.post_json("/api/auth/verify-totp-login", {"totp": otp})
    if status != 200:
        return False
    if not verify.get("require_device_approval"):
        return True

    status, pending = client.get_json(f"/api/auth/login/pending?user_id={user_id}")
    if status != 200 or pending.get("status") != "pending":
        return False

    nonce = pending.get("nonce", "")
    signature = sign_payload(key, nonce, device_id, rp_id, otp)
    status, approval = client.post_json(
        "/api/auth/login/approve",
        {
            "login_id": pending.get("login_id"),
            "device_id": device_id,
            "rp_id": rp_id,
            "otp": otp,
            "nonce": nonce,
            "signature": signature,
        },
    )
    return status == 200 and approval.get("status") == "ok"


def otp_with_drift(secret: str, drift_seconds: int) -> str:
    now = int(time.time())
    return pyotp.TOTP(secret).at(now - drift_seconds)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://example.local")
    parser.add_argument("--identifier", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification (dev only).")
    parser.add_argument("--trials", type=int, default=30)
    parser.add_argument("--drifts", default="0,15,30,60,90,120")
    parser.add_argument("--output", default="experiments/iam_frr_sweep.csv")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    client = IamClient(args.base_url, args.insecure)

    run_id = uuid.uuid4().hex[:8]
    user_id, device_id, rp_id, secret, key = enroll_device(
        client, args.identifier, args.password
    )
    drifts = [int(x.strip()) for x in args.drifts.split(",") if x.strip()]

    rows = []
    for drift in drifts:
        ok_totp = 0
        ok_zt = 0
        for _ in range(args.trials):
            otp = otp_with_drift(secret, drift)
            if totp_verify(client, otp):
                ok_totp += 1
            if zt_verify(client, user_id, device_id, rp_id, otp, key):
                ok_zt += 1
        rows.append((drift, ok_totp, ok_zt, args.trials))

    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["drift_seconds", "standard_totp_ok", "zt_totp_ok", "total"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.output} (run {run_id})")


if __name__ == "__main__":
    main()
