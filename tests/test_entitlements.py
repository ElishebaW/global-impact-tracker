"""Tests for Pro tier entitlement gating."""

from __future__ import annotations

import datetime as dt
import importlib
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from global_impact_tracker import entitlements
from conftest import src_env


def _sign(customer_id: str, expiry: str) -> str:
    payload = entitlements._build_payload(customer_id, expiry)
    signature = entitlements._sign_payload(payload)
    return f"gip-{customer_id}-{expiry}-{signature}"


@pytest.fixture(autouse=True)
def _reload_entitlements():
    importlib.reload(entitlements)
    with mock.patch.object(entitlements, "_SIGNING_KEY", "test-signing-secret"):
        yield


class TestVerifyLicenseKey:
    def test_valid_unexpired_key_returns_true(self):
        key = _sign("acme", "20991231")
        assert entitlements.verify_license_key(key, today=dt.date(2026, 4, 23)) is True

    def test_tampered_signature_returns_false(self):
        key = _sign("acme", "20991231")
        tampered = f"{key[:-1]}0"
        assert entitlements.verify_license_key(tampered, today=dt.date(2026, 4, 23)) is False

    def test_tampered_customer_id_returns_false(self):
        key = _sign("acme", "20991231").replace("gip-acme-", "gip-other-", 1)
        assert entitlements.verify_license_key(key, today=dt.date(2026, 4, 23)) is False

    def test_tampered_expiry_returns_false(self):
        key = _sign("acme", "20991231").replace("-20991231-", "-20990101-", 1)
        assert entitlements.verify_license_key(key, today=dt.date(2026, 4, 23)) is False

    def test_malformed_expiry_returns_false(self):
        key = _sign("acme", "20991231").replace("20991231", "20260230", 1)
        assert entitlements.verify_license_key(key, today=dt.date(2026, 4, 23)) is False

    def test_expired_key_returns_false(self):
        key = _sign("acme", "20260422")
        assert entitlements.verify_license_key(key, today=dt.date(2026, 4, 23)) is False

    def test_wrong_prefix_returns_false(self):
        key = _sign("acme", "20991231").replace("gip-", "git-", 1)
        assert entitlements.verify_license_key(key, today=dt.date(2026, 4, 23)) is False

    def test_wrong_segment_count_returns_false(self):
        assert entitlements.verify_license_key("gip-acme-20991231", today=dt.date(2026, 4, 23)) is False

    def test_empty_key_parts_return_false(self):
        assert entitlements.verify_license_key("gip--20991231-deadbeef", today=dt.date(2026, 4, 23)) is False
        assert entitlements.verify_license_key("gip-acme--deadbeef", today=dt.date(2026, 4, 23)) is False
        assert entitlements.verify_license_key("gip-acme-20991231-", today=dt.date(2026, 4, 23)) is False

    def test_old_three_part_key_format_returns_false(self):
        assert entitlements.verify_license_key("git-deadbeef-0123456789abcdef", today=dt.date(2026, 4, 23)) is False

    def test_signature_must_be_exactly_64_lowercase_hex_characters(self):
        assert entitlements.verify_license_key("gip-acme-20991231-abc123", today=dt.date(2026, 4, 23)) is False
        uppercase_sig = "A" * 64
        assert entitlements.verify_license_key(
            f"gip-acme-20991231-{uppercase_sig}",
            today=dt.date(2026, 4, 23),
        ) is False

    def test_placeholder_signing_key_rejects_all_keys(self):
        key = _sign("acme", "20991231")
        with mock.patch.object(entitlements, "_SIGNING_KEY", entitlements._PLACEHOLDER_SIGNING_KEY):
            assert entitlements.verify_license_key(key, today=dt.date(2026, 4, 23)) is False


class TestIsPro:
    def test_missing_env_var_returns_false(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            assert entitlements.is_pro() is False

    def test_empty_env_var_returns_false(self):
        with mock.patch.dict(os.environ, {"IMPACT_TRACKER_LICENSE_KEY": "   "}):
            assert entitlements.is_pro() is False

    def test_valid_env_var_returns_true(self):
        with mock.patch.dict(os.environ, {"IMPACT_TRACKER_LICENSE_KEY": _sign("acme", "20991231")}):
            assert entitlements.is_pro() is True


class TestGenerateKeyScript:
    def test_generated_key_matches_verifier(self):
        result = subprocess.run(
            [
                sys.executable,
                "tools/generate_key.py",
                "acme",
                "20991231",
            ],
            cwd=Path(__file__).parent.parent,
            env={**src_env(), "IMPACT_TRACKER_SIGNING_SECRET": "test-signing-secret"},
            check=True,
            capture_output=True,
            text=True,
        )
        key = result.stdout.strip()
        assert entitlements.verify_license_key(key, today=dt.date(2026, 4, 23)) is True
