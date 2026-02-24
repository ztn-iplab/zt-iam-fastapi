#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import ssl
from pathlib import Path
from typing import Any
from urllib import error, parse, request


ABS_PATH_RE = re.compile(r"(/Users/[^/\s]+(?:/[^\s]+)*)")
HOSTLIKE_RE = re.compile(r"\b([A-Za-z0-9._-]+\.(?:localdomain|local|lan|home|internal))\b")


class ApiClient:
    def __init__(self, base_url: str, api_key: str, insecure: bool = False) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        ctx = ssl._create_unverified_context() if insecure else None
        handlers = []
        if ctx:
            handlers.append(request.HTTPSHandler(context=ctx))
        self.opener = request.build_opener(*handlers)

    def get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        suffix = "?" + parse.urlencode({k: v for k, v in params.items() if v is not None})
        req = request.Request(
            f"{self.base_url}{path}{suffix}",
            method="GET",
            headers={"X-API-Key": self.api_key},
        )
        try:
            with self.opener.open(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            raise RuntimeError(f"HTTP {exc.code}: {raw}") from exc


def stable_token(value: Any, prefix: str) -> str | None:
    if value in (None, ""):
        return None
    raw = str(value).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()[:12]
    return f"{prefix}_{digest}"


def sanitize_str(s: str) -> str:
    s = ABS_PATH_RE.sub("<ABS_PATH>", s)
    s = HOSTLIKE_RE.sub("<LOCAL_HOST>", s)
    # redact long API-key-like tokens
    s = re.sub(r"\b[A-Z0-9]{8,}-[A-Za-z0-9]{8,}\b", "<REDACTED_TOKEN>", s)
    s = re.sub(r"\b[a-f0-9]{32,}\b", "<REDACTED_HEX>", s, flags=re.IGNORECASE)
    return s


def redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return redact_dict(value)
    if isinstance(value, list):
        return [redact_value(v) for v in value]
    if isinstance(value, str):
        return sanitize_str(value)
    return value


def redact_dict(d: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in d.items():
        lk = k.lower()
        if lk in {"tenant_id"}:
            out[k] = "<REDACTED_TENANT_ID>"
            continue
        if lk in {"user_id"}:
            out[k] = stable_token(v, "user")
            continue
        if lk in {"session_id", "correlation_id", "experiment_run_id"}:
            out[k] = stable_token(v, lk)
            continue
        if lk in {"actor_label", "session_label", "source_ref"}:
            out[k] = stable_token(v, lk)
            continue
        if lk in {"mobile_number", "msisdn"}:
            out[k] = "<REDACTED_MSISDN>" if v not in (None, "") else None
            continue
        if lk in {"iccid", "old_iccid", "new_iccid"}:
            out[k] = stable_token(v, "iccid")
            continue
        if lk in {"ip_address", "remote_addr"}:
            out[k] = "<REDACTED_IP>" if v not in (None, "") else None
            continue
        if lk in {"device_info", "user_agent"}:
            out[k] = "<REDACTED_UA>" if v not in (None, "") else None
            continue
        out[k] = redact_value(v)
    return out


def redact_trace(data: dict[str, Any]) -> dict[str, Any]:
    redacted = redact_dict(data)
    if isinstance(redacted.get("filters"), dict):
        redacted["filters"] = redact_dict(redacted["filters"])
    return redacted


def main() -> None:
    parser = argparse.ArgumentParser(description="Export and sanitize AIg trace JSON for sharing")
    parser.add_argument("--trace-json", help="Local raw trace JSON to sanitize")
    parser.add_argument("--base-url", default="https://localhost/api/v1")
    parser.add_argument("--api-key", help="Tenant API key (required when fetching from API)")
    parser.add_argument("--insecure", action="store_true")
    parser.add_argument("--experiment-run-id")
    parser.add_argument("--correlation-id")
    parser.add_argument("--output", required=True, help="Sanitized output JSON path")
    args = parser.parse_args()

    if not args.trace_json:
        if not args.api_key:
            raise SystemExit("--api-key is required when fetching from API")
        if not (args.experiment_run_id or args.correlation_id):
            raise SystemExit("Provide --experiment-run-id or --correlation-id when fetching from API")
        client = ApiClient(args.base_url, args.api_key, insecure=args.insecure)
        raw = client.get_json(
            "/aig/traces/export",
            {
                "experiment_run_id": args.experiment_run_id,
                "correlation_id": args.correlation_id,
                "limit_per_stream": 10000,
            },
        )
    else:
        raw = json.loads(Path(args.trace_json).read_text(encoding="utf-8"))

    sanitized = redact_trace(raw)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sanitized, indent=2), encoding="utf-8")
    print(f"Wrote sanitized trace: {out}")


if __name__ == "__main__":
    main()

