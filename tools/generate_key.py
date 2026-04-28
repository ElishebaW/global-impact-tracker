"""Generate a valid HMAC-signed Pro license key.

Usage:
    export IMPACT_TRACKER_SIGNING_SECRET=<matching_signing_key>
    python3 tools/generate_key.py <customer_id> <expiry_yyyymmdd>

Keep this file in the private repo only. The public repo should continue to
exclude `tools/`, and the signing key must never be committed in plaintext.
"""

from __future__ import annotations

import datetime as dt
import hmac
import os
import re
import sys

from global_impact_tracker.entitlements import _KEY_PREFIX, _build_payload


def _parse_expiry(expiry: str) -> str:
    if not re.fullmatch(r"\d{8}", expiry):
        raise SystemExit("expiry must be in YYYYMMDD format")
    try:
        dt.datetime.strptime(expiry, "%Y%m%d")
    except ValueError as exc:
        raise SystemExit("expiry must be a valid YYYYMMDD date") from exc
    return expiry


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("usage: python3 tools/generate_key.py <customer_id> <expiry_yyyymmdd>")

    _, customer_id, expiry = argv
    if not customer_id:
        raise SystemExit("customer_id is required")

    signing_secret = os.environ.get("IMPACT_TRACKER_SIGNING_SECRET", "")
    if not signing_secret:
        raise SystemExit("IMPACT_TRACKER_SIGNING_SECRET env var is required")

    expiry = _parse_expiry(expiry)
    payload = _build_payload(customer_id, expiry)
    signature = hmac.new(signing_secret.encode(), payload.encode(), "sha256").hexdigest()
    print(f"{_KEY_PREFIX}-{customer_id}-{expiry}-{signature}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
