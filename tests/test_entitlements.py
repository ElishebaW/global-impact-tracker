"""Tests for Pro tier entitlement gating."""

import importlib
import os
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


class TestIsProStaticKeys:
    def test_no_key_returns_false(self):
        import entitlements
        with mock.patch.dict(os.environ, {}, clear=True):
            os.environ.pop("STRIPE_LICENSE_KEY", None)
            assert entitlements.is_pro() is False

    def test_invalid_key_returns_false(self):
        import entitlements
        with mock.patch.dict(os.environ, {"STRIPE_LICENSE_KEY": "bad-key"}):
            assert entitlements.is_pro() is False

    def test_empty_key_returns_false(self):
        import entitlements
        with mock.patch.dict(os.environ, {"STRIPE_LICENSE_KEY": "   "}):
            assert entitlements.is_pro() is False

    def test_valid_static_key_returns_true(self):
        import entitlements
        test_key = "test_static_key_abc123_phase4_unit"
        entitlements._VALID_KEYS.add(test_key)
        try:
            with mock.patch.dict(os.environ, {"STRIPE_LICENSE_KEY": test_key}):
                assert entitlements.is_pro() is True
        finally:
            entitlements._VALID_KEYS.discard(test_key)


class TestIsProFileKeys:
    def test_key_in_valid_keys_file_returns_true(self, tmp_path, monkeypatch):
        tracker_dir = tmp_path / ".impact_tracker"
        tracker_dir.mkdir()
        (tracker_dir / "valid_keys.txt").write_text("file-key-xyz789\n")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        import entitlements
        importlib.reload(entitlements)
        with mock.patch.dict(os.environ, {"STRIPE_LICENSE_KEY": "file-key-xyz789"}):
            assert entitlements.is_pro() is True

    def test_key_not_in_file_returns_false(self, tmp_path, monkeypatch):
        tracker_dir = tmp_path / ".impact_tracker"
        tracker_dir.mkdir()
        (tracker_dir / "valid_keys.txt").write_text("other-key\n")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        import entitlements
        importlib.reload(entitlements)
        with mock.patch.dict(os.environ, {"STRIPE_LICENSE_KEY": "file-key-xyz789"}):
            assert entitlements.is_pro() is False

    def test_missing_keys_file_does_not_raise(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        import entitlements
        importlib.reload(entitlements)
        with mock.patch.dict(os.environ, {"STRIPE_LICENSE_KEY": "any-key"}):
            assert entitlements.is_pro() is False

    def test_blank_lines_in_file_ignored(self, tmp_path, monkeypatch):
        tracker_dir = tmp_path / ".impact_tracker"
        tracker_dir.mkdir()
        (tracker_dir / "valid_keys.txt").write_text("\n  \nreal-key\n\n")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        import entitlements
        importlib.reload(entitlements)
        with mock.patch.dict(os.environ, {"STRIPE_LICENSE_KEY": "real-key"}):
            assert entitlements.is_pro() is True
