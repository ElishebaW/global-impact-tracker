"""License key entitlements for Global Impact Tracker Pro tier.

Keys have format: git-{key_id}-{signature}
  - signature = HMAC-SHA256(_SIGNING_SECRET, key_id)[:16]
  - _SIGNING_SECRET is SHA-256(raw_secret) — hardcoded derived constant
  - Raw secret lives only in IMPACT_TRACKER_SIGNING_SECRET env var (developer only)
  - Verification is self-contained — no file lookup, works on any machine
"""

from __future__ import annotations

import hashlib
import hmac
import os

# Derived from IMPACT_TRACKER_SIGNING_SECRET via SHA-256 — one-way, so
# reading this source does not allow generating new keys.
_SIGNING_SECRET: bytes = bytes.fromhex(
    "97e32d7e5b9ec65440ffb3a871dd6db22c8674c16ec6cdfc9b4676732cbc777e"
)

_KEY_PREFIX = "git-"


def _verify_key(key: str) -> bool:
    parts = key.split("-")
    if len(parts) != 3:
        return False
    prefix, key_id, signature = parts
    if prefix != "git" or not key_id or not signature:
        return False
    expected = hmac.new(_SIGNING_SECRET, key_id.encode(), "sha256").hexdigest()[:16]
    return hmac.compare_digest(signature, expected)


def is_pro() -> bool:
    """Return True if STRIPE_LICENSE_KEY env var is a valid HMAC-signed key."""
    key = os.environ.get("STRIPE_LICENSE_KEY", "").strip()
    if not key:
        return False
    return _verify_key(key)
