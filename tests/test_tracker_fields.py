"""Tests for Phase 3 — extended nullable fields and Dollars_Saved auto-compute."""

import csv
from pathlib import Path

import pytest

from global_impact_tracker.tracker import GlobalImpactTracker


def _make_tracker(tmpdir: Path) -> GlobalImpactTracker:
    t = GlobalImpactTracker.__new__(GlobalImpactTracker)
    t.log_dir = tmpdir
    t.log_file = tmpdir / "test.csv"
    t.metrics_file = tmpdir / "metrics.json"
    t._ensure_log_exists()
    return t


def _read_row(log_file: Path, index: int = 0) -> dict[str, str]:
    with open(log_file) as f:
        return list(csv.DictReader(f))[index]


# ── Nullable fields default to empty ─────────────────────────────────────────

class TestNullableFieldDefaults:
    def test_task_type_defaults_empty(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0)
        assert _read_row(t.log_file)["Task_Type"] == ""

    def test_complexity_defaults_empty(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0)
        assert _read_row(t.log_file)["Complexity"] == ""

    def test_tools_used_defaults_empty(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0)
        assert _read_row(t.log_file)["Tools_Used"] == ""

    def test_audience_defaults_empty(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0)
        assert _read_row(t.log_file)["Audience"] == ""

    def test_token_usage_defaults_empty(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0)
        assert _read_row(t.log_file)["Token_Usage"] == ""


# ── Nullable fields write correctly when provided ─────────────────────────────

class TestNullableFieldsWritten:
    def test_task_type_written(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0, task_type="feature")
        assert _read_row(t.log_file)["Task_Type"] == "feature"

    def test_complexity_written(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0, complexity="high")
        assert _read_row(t.log_file)["Complexity"] == "high"

    def test_tools_used_written(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0, tools_used="claude|windsurf")
        assert _read_row(t.log_file)["Tools_Used"] == "claude|windsurf"

    def test_audience_written(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0, audience="recruiter")
        assert _read_row(t.log_file)["Audience"] == "recruiter"

    def test_token_usage_written(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0, token_usage=4200)
        assert _read_row(t.log_file)["Token_Usage"] == "4200"


# ── Dollars_Saved auto-compute ────────────────────────────────────────────────

class TestDollarsSavedAutoCompute:
    def test_auto_compute_when_not_provided(self, tmp_path):
        t = _make_tracker(tmp_path)
        # baseline_hrs=2.0, ai_sec=3600 (1hr) → hours_saved=1.0 → $88.46
        t.log_impact("proj", "task", 2.0, 3600.0)
        dollars = float(_read_row(t.log_file)["Dollars_Saved"])
        assert dollars == pytest.approx(88.46, rel=1e-3)

    def test_auto_compute_zero_when_ai_exceeds_baseline(self, tmp_path):
        t = _make_tracker(tmp_path)
        # baseline_hrs=0.1, ai_sec=7200 (2hrs) → hours_saved clamped to 0 → $0.00
        t.log_impact("proj", "task", 0.1, 7200.0)
        dollars = float(_read_row(t.log_file)["Dollars_Saved"])
        assert dollars == 0.0

    def test_manual_override_respected(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 2.0, 3600.0, dollars_saved=500.0)
        dollars = float(_read_row(t.log_file)["Dollars_Saved"])
        assert dollars == 500.0

    def test_manual_override_zero_not_overwritten(self, tmp_path):
        t = _make_tracker(tmp_path)
        # Explicit 0.0 override should be kept, not auto-computed
        t.log_impact("proj", "task", 2.0, 60.0, dollars_saved=0.0)
        dollars = float(_read_row(t.log_file)["Dollars_Saved"])
        assert dollars == 0.0


# ── Column count matches schema ───────────────────────────────────────────────

class TestColumnSchema:
    def test_header_has_12_columns(self, tmp_path):
        t = _make_tracker(tmp_path)
        with open(t.log_file) as f:
            headers = next(csv.reader(f))
        assert len(headers) == 12

    def test_data_row_has_12_columns(self, tmp_path):
        t = _make_tracker(tmp_path)
        t.log_impact("proj", "task", 1.0, 60.0)
        with open(t.log_file) as f:
            rows = list(csv.reader(f))
        assert len(rows[1]) == 12
