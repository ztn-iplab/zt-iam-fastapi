import argparse
import base64
import csv
import json
import os
import ssl
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Tuple
from urllib import error, parse, request

import pyotp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


@dataclass
class Enrollment:
    user_id: str
    device_id: str
    rp_id: str
    secret: str
    recovery_codes: list[str]
    private_key: ec.EllipticCurvePrivateKey
    identifier: str


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


def enroll_device(client: IamClient, identifier: str, password: str) -> Enrollment:
    status, _ = client.post_json(
        "/api/auth/login",
        {"identifier": identifier, "password": password},
    )
    if status != 200:
        raise RuntimeError(f"Login failed: status={status}")

    status, setup = client.get_json("/api/auth/setup-totp?include_payload=1")
    if status != 200 or "manual_key" not in setup:
        raise RuntimeError(f"Setup TOTP failed: status={status} body={setup}")

    payload = setup.get("payload")
    if not payload:
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
            "device_label": payload.get("device_label") or "IAM Experiment Device",
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
    recovery_codes = register.get("recovery_codes") or []
    return Enrollment(
        user_id=user_id,
        device_id=device_id,
        rp_id=payload["rp_id"],
        secret=secret,
        recovery_codes=recovery_codes,
        private_key=private_key,
        identifier=identifier,
    )


def totp_verify(client: IamClient, otp: str) -> Tuple[bool, str]:
    status, data = client.post_json("/api/auth/verify-totp", {"code": otp})
    if status == 200:
        return True, "ok"
    return False, data.get("detail") or data.get("error") or f"status_{status}"


def login_recover(client: IamClient, identifier: str, code: str) -> Tuple[bool, str]:
    payload = {"email": identifier, "recovery_code": code}
    status, data = client.post_json("/api/auth/login/recover", payload)
    if status == 200 and data.get("status") == "ok":
        return True, "ok"
    return False, data.get("reason") or data.get("detail") or f"status_{status}"


def rotate_key(
    client: IamClient,
    enrollment: Enrollment,
    public_key_b64: str,
    key_type: str = "p256",
) -> Tuple[bool, str, float]:
    started = time.perf_counter()
    status, data = client.post_json(
        "/api/auth/zt/rotate-key",
        {
            "device_id": enrollment.device_id,
            "rp_id": enrollment.rp_id,
            "key_type": key_type,
            "public_key": public_key_b64,
        },
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    if status == 200 and data.get("status") == "ok":
        return True, "ok", elapsed_ms
    return False, data.get("detail") or data.get("reason") or f"status_{status}", elapsed_ms


def zt_verify(
    client: IamClient,
    enrollment: Enrollment,
    otp: str,
    key: ec.EllipticCurvePrivateKey,
) -> Tuple[bool, str]:
    status, verify = client.post_json("/api/auth/verify-totp-login", {"totp": otp})
    if status != 200:
        return False, verify.get("detail") or verify.get("error") or f"status_{status}"
    if not verify.get("require_device_approval"):
        return True, "ok"

    status, pending = client.get_json(f"/api/auth/login/pending?user_id={enrollment.user_id}")
    if status != 200 or pending.get("status") != "pending":
        return False, pending.get("reason") or f"status_{status}"

    nonce = pending.get("nonce", "")
    rp_id = pending.get("rp_id", "")
    device_id = str(pending.get("device_id", ""))
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
    if status == 200 and approval.get("status") == "ok":
        return True, "ok"
    return False, approval.get("reason") or f"status_{status}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://localhost.localdomain.com")
    parser.add_argument("--identifier", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification (dev only).")
    parser.add_argument("--output", default="experiments/iam_metrics.csv")
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--recovery-trials", type=int, default=8)
    parser.add_argument("--rebind-trials", type=int, default=8)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    client = IamClient(args.base_url, args.insecure)

    run_id = uuid.uuid4().hex[:8]
    enrollment = enroll_device(client, args.identifier, args.password)
    attacker_key, _ = generate_keypair()

    rows: list[tuple[str, str, bool, str, float]] = []
    for _ in range(args.rebind_trials):
        new_key, new_pub = generate_keypair()
        ok, reason, rotate_ms = rotate_key(client, enrollment, new_pub)
        if ok:
            otp = pyotp.TOTP(enrollment.secret).now()
            start = time.perf_counter()
            ok, reason = zt_verify(client, enrollment, otp, new_key)
            verify_ms = (time.perf_counter() - start) * 1000
            total_ms = rotate_ms + verify_ms
            rows.append(("rebind_time", "zt_totp", ok, reason, total_ms))
            if ok:
                enrollment.private_key = new_key
        else:
            rows.append(("rebind_time", "zt_totp", False, reason, rotate_ms))

    scenarios = [
        ("legitimate_login", enrollment.private_key),
        ("seed_compromise", attacker_key),
        ("relay_phishing", attacker_key),
    ]
    for scenario, key in scenarios:
        for _ in range(args.trials):
            otp = pyotp.TOTP(enrollment.secret).now()
            start = time.perf_counter()
            ok, reason = totp_verify(client, otp)
            duration = (time.perf_counter() - start) * 1000
            rows.append((scenario, "standard_totp", ok, reason, duration))

            start = time.perf_counter()
            ok, reason = zt_verify(client, enrollment, otp, key)
            duration = (time.perf_counter() - start) * 1000
            rows.append((scenario, "zt_totp", ok, reason, duration))

    recovery_trials = min(args.recovery_trials, len(enrollment.recovery_codes))
    for i in range(recovery_trials):
        otp = pyotp.TOTP(enrollment.secret).now()
        start = time.perf_counter()
        ok, reason = totp_verify(client, otp)
        duration = (time.perf_counter() - start) * 1000
        rows.append(("offline_degraded", "standard_totp", ok, reason, duration))

        code = enrollment.recovery_codes[i]
        start = time.perf_counter()
        ok, reason = login_recover(client, enrollment.identifier, code)
        duration = (time.perf_counter() - start) * 1000
        rows.append(("offline_degraded", "zt_totp", ok, reason, duration))

        start = time.perf_counter()
        ok, reason = login_recover(client, enrollment.identifier, code)
        duration = (time.perf_counter() - start) * 1000
        rows.append(("offline_replay", "zt_totp", ok, reason, duration))

    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scenario", "mode", "ok", "reason", "latency_ms"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.output}")
    print(f"Run ID: {run_id}  Timestamp: {datetime.utcnow().isoformat()}Z")


if __name__ == "__main__":
    main()
