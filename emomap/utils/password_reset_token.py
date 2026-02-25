import base64
import binascii
import hashlib
import hmac
import json
from datetime import datetime


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_password_reset_token(
    token_id: int,
    user_id: int,
    expires_at: datetime,
    secret: str,
) -> str:
    payload = {
        "tid": token_id,
        "uid": user_id,
        "exp": int(expires_at.timestamp()),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
    return f"{_b64url_encode(payload_bytes)}.{_b64url_encode(signature)}"


def verify_password_reset_token(token: str, secret: str) -> dict:
    try:
        payload_b64, signature_b64 = token.split(".", maxsplit=1)
        payload_bytes = _b64url_decode(payload_b64)
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).digest()
        provided_signature = _b64url_decode(signature_b64)
        if not hmac.compare_digest(expected_signature, provided_signature):
            raise ValueError("Invalid reset token")

        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, json.JSONDecodeError, binascii.Error) as exc:
        raise ValueError("Invalid reset token") from exc

    exp = payload.get("exp")
    if not isinstance(exp, int):
        raise ValueError("Invalid reset token")

    if datetime.utcnow().timestamp() >= exp:
        raise ValueError("Reset token has expired")

    return payload
