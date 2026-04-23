"""License key entitlements for Global Impact Tracker Pro tier."""

from __future__ import annotations

import datetime as dt
import hmac
import os
import re

_PLACEHOLDER_SIGNING_KEY = "PUBLIC_REPO_PLACEHOLDER_DO_NOT_USE"
_SIGNING_KEY = _PLACEHOLDER_SIGNING_KEY
_KEY_PREFIX = "gip"
_SIGNATURE_RE = re.compile(r"[0-9a-f]{64}")


def _is_placeholder_signing_key() -> bool:
    return _SIGNING_KEY == _PLACEHOLDER_SIGNING_KEY


def _build_payload(customer_id: str, expiry: str) -> str:
    return f"{customer_id}-{expiry}"


def _sign_payload(payload: str) -> str:
    return hmac.new(_SIGNING_KEY.encode(), payload.encode(), "sha256").hexdigest()


def _parse_expiry(expiry: str) -> dt.date | None:
    if not re.fullmatch(r"\d{8}", expiry):
        return None
    try:
        return dt.datetime.strptime(expiry, "%Y%m%d").date()
    except ValueError:
        return None


def _is_valid_signature(signature: str) -> bool:
    return bool(_SIGNATURE_RE.fullmatch(signature))


def verify_license_key(key: str, *, today: dt.date | None = None) -> bool:
    """Return True when a signed key is valid and unexpired."""
    if _is_placeholder_signing_key():
        return False

    parts = key.split("-")
    if len(parts) != 4:
        return False

    prefix, customer_id, expiry, signature = parts
    if prefix != _KEY_PREFIX:
        return False
    if not customer_id or not expiry or not signature:
        return False
    if not _is_valid_signature(signature):
        return False

    expiry_date = _parse_expiry(expiry)
    if expiry_date is None:
        return False

    current_date = today or dt.date.today()
    if expiry_date < current_date:
        return False

    expected_signature = _sign_payload(_build_payload(customer_id, expiry))
    return hmac.compare_digest(signature, expected_signature)


def is_pro() -> bool:
    """Return True if IMPACT_TRACKER_LICENSE_KEY contains a valid Pro key."""
    key = os.environ.get("IMPACT_TRACKER_LICENSE_KEY", "").strip()
    if not key:
        return False
    return verify_license_key(key)
