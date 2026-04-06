"""License key entitlements for Global Impact Tracker Pro tier.

Architecture: _VALID_KEYS is a static set for the MVP. When user base grows,
swap _check_key() to an HTTP call against a validation endpoint without
changing the public is_pro() interface.
"""

from __future__ import annotations

import os
from pathlib import Path

# Add issued Stripe license keys here as customers purchase.
# Format: plain string, minimum 32 chars (secrets.token_urlsafe(32)).
# Do NOT commit actual customer keys to git — use ~/.impact_tracker/valid_keys.txt
# for production keys (see is_pro() implementation).
_VALID_KEYS: set[str] = set()


def is_pro() -> bool:
    """Return True if STRIPE_LICENSE_KEY env var matches a known valid key.

    Checks two sources:
    1. _VALID_KEYS set in this file (for test keys and early-access keys)
    2. ~/.impact_tracker/valid_keys.txt — one key per line, not committed to git
       (production keys are written here by the manual delivery process)
    """
    key = os.environ.get("STRIPE_LICENSE_KEY", "").strip()
    if not key:
        return False
    if key in _VALID_KEYS:
        return True
    keys_file = Path.home() / ".impact_tracker" / "valid_keys.txt"
    if keys_file.exists():
        valid = {line.strip() for line in keys_file.read_text().splitlines() if line.strip()}
        return key in valid
    return False
