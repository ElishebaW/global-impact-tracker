"""Tests for Pro tier entitlement gating — HMAC signed keys."""

import hashlib
import hmac
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

import entitlements


@pytest.fixture
def make_valid_key(monkeypatch):
    test_secret = hashlib.sha256(b"test-only-secret").digest()
    monkeypatch.setattr(entitlements, "_SIGNING_SECRET", test_secret)

    def _make(key_id: str = "abc12345") -> str:
        sig = hmac.new(test_secret, key_id.encode(), "sha256").hexdigest()[:16]
        return f"git-{key_id}-{sig}"

    return _make


class TestIsProHMACVerification:
    def test_valid_key_returns_true(self, monkeypatch, make_valid_key):
        key = make_valid_key()
        monkeypatch.setenv("STRIPE_LICENSE_KEY", key)
        assert entitlements.is_pro() is True

    def test_tampered_signature_returns_false(self, monkeypatch, make_valid_key):
        key = make_valid_key()
        parts = key.split("-")
        parts[2] = "0000000000000000"
        monkeypatch.setenv("STRIPE_LICENSE_KEY", "-".join(parts))
        assert entitlements.is_pro() is False

    def test_tampered_key_id_returns_false(self, monkeypatch, make_valid_key):
        key = make_valid_key()
        parts = key.split("-")
        parts[1] = "ffffffff"
        monkeypatch.setenv("STRIPE_LICENSE_KEY", "-".join(parts))
        assert entitlements.is_pro() is False

    def test_wrong_prefix_returns_false(self, monkeypatch, make_valid_key):
        key = make_valid_key()
        bad_key = "pro-" + "-".join(key.split("-")[1:])
        monkeypatch.setenv("STRIPE_LICENSE_KEY", bad_key)
        assert entitlements.is_pro() is False

    def test_too_few_segments_returns_false(self, monkeypatch):
        monkeypatch.setenv("STRIPE_LICENSE_KEY", "git-abc123")
        assert entitlements.is_pro() is False

    def test_too_many_segments_returns_false(self, monkeypatch):
        monkeypatch.setenv("STRIPE_LICENSE_KEY", "git-a-b-c")
        assert entitlements.is_pro() is False

    def test_empty_env_var_returns_false(self, monkeypatch):
        monkeypatch.setenv("STRIPE_LICENSE_KEY", "")
        assert entitlements.is_pro() is False

    def test_whitespace_only_env_var_returns_false(self, monkeypatch):
        monkeypatch.setenv("STRIPE_LICENSE_KEY", "   ")
        assert entitlements.is_pro() is False

    def test_missing_env_var_returns_false(self, monkeypatch):
        monkeypatch.delenv("STRIPE_LICENSE_KEY", raising=False)
        assert entitlements.is_pro() is False

    def test_empty_key_id_returns_false(self, monkeypatch):
        monkeypatch.setenv("STRIPE_LICENSE_KEY", "git--somesig123456")
        assert entitlements.is_pro() is False

    def test_empty_signature_returns_false(self, monkeypatch):
        monkeypatch.setenv("STRIPE_LICENSE_KEY", "git-someid-")
        assert entitlements.is_pro() is False

    def test_random_string_no_dashes_returns_false(self, monkeypatch):
        monkeypatch.setenv("STRIPE_LICENSE_KEY", "notavalidkeyatall")
        assert entitlements.is_pro() is False
