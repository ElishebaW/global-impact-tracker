"""Integration tests for MCP Pro gating through shared entitlements."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

from global_impact_tracker import entitlements
from global_impact_tracker.tracker import GlobalImpactTracker
from conftest import src_env


def _make_tracker(tmpdir: Path) -> GlobalImpactTracker:
    tracker = GlobalImpactTracker.__new__(GlobalImpactTracker)
    tracker.log_dir = tmpdir
    tracker.log_file = tmpdir / "test.csv"
    tracker.metrics_file = tmpdir / "metrics.json"
    tracker._ensure_log_exists()
    return tracker


def _load_server_module():
    server_path = Path(__file__).parent.parent / "mcp" / "server.py"
    spec = importlib.util.spec_from_file_location("test_mcp_server", server_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _generate_key(customer_id: str, expiry: str) -> str:
    result = subprocess.run(
        [sys.executable, "tools/generate_key.py", customer_id, expiry],
        cwd=Path(__file__).parent.parent,
        env={**src_env(), "IMPACT_TRACKER_SIGNING_SECRET": "test-signing-secret"},
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class TestMcpLicensing:
    def test_paid_log_task_succeeds_with_valid_generated_key(self, monkeypatch, tmp_path):
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
        monkeypatch.setenv("IMPACT_TRACKER_LICENSE_KEY", _generate_key("acme", "20991231"))
        monkeypatch.setattr(entitlements, "_SIGNING_KEY", "test-signing-secret")

        server = _load_server_module()
        server.tracker = _make_tracker(tmp_path)
        monkeypatch.setattr(server, "_estimate_with_gemini", lambda task, context: {
            "baseline_hours": 2.5,
            "ai_seconds": 45.0,
            "reasoning": "stubbed",
        })

        result = server.log_task(project="proj", task="ship feature", context="implemented and tested")

        assert "Logged: [proj] ship feature" in result
        assert "Baseline: 2.5h | AI: 45.0s" in result

    def test_paid_log_task_is_blocked_for_invalid_or_expired_key(self, monkeypatch, tmp_path):
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
        monkeypatch.setenv("IMPACT_TRACKER_LICENSE_KEY", _generate_key("acme", "20260422"))
        monkeypatch.setattr(entitlements, "_SIGNING_KEY", "test-signing-secret")

        server = _load_server_module()
        server.tracker = _make_tracker(tmp_path)
        monkeypatch.setattr(server, "_estimate_with_gemini", lambda task, context: {
            "baseline_hours": 2.5,
            "ai_seconds": 45.0,
            "reasoning": "stubbed",
        })

        result = server.log_task(project="proj", task="ship feature", context="implemented and tested")

        assert "Pro tier required for AI estimation" in result
