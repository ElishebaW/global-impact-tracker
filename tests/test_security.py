"""Tests for security hardening — Phase 2.5."""

import csv
from pathlib import Path

from global_impact_tracker.tracker import GlobalImpactTracker, _sanitize_csv_field


# ── CSV injection sanitization ────────────────────────────────────────────────

class TestSanitizeCsvField:
    # Standard formula prefixes
    def test_formula_prefix_equals(self):
        assert _sanitize_csv_field("=SUM(A1)").startswith("\t")

    def test_formula_prefix_at(self):
        assert _sanitize_csv_field("@echo").startswith("\t")

    def test_formula_prefix_plus(self):
        assert _sanitize_csv_field("+1234").startswith("\t")

    def test_formula_prefix_minus(self):
        assert _sanitize_csv_field("-1234").startswith("\t")

    # Whitespace control characters (OWASP: tab 0x09, CR 0x0D, LF 0x0A)
    def test_formula_prefix_tab(self):
        assert _sanitize_csv_field("\t=hidden formula").startswith("\t\t")

    def test_formula_prefix_carriage_return(self):
        assert _sanitize_csv_field("\r=hidden").startswith("\t")

    def test_formula_prefix_line_feed(self):
        assert _sanitize_csv_field("\n=hidden").startswith("\t")

    # Full-width Unicode variants (OWASP: Japanese locale attacks)
    def test_formula_prefix_fullwidth_equals(self):
        assert _sanitize_csv_field("＝SUM(A1)").startswith("\t")

    def test_formula_prefix_fullwidth_plus(self):
        assert _sanitize_csv_field("＋value").startswith("\t")

    def test_formula_prefix_fullwidth_minus(self):
        assert _sanitize_csv_field("－value").startswith("\t")

    def test_formula_prefix_fullwidth_at(self):
        assert _sanitize_csv_field("＠user").startswith("\t")

    # Safe values
    def test_safe_string_unchanged(self):
        assert _sanitize_csv_field("normal task description") == "normal task description"

    def test_none_passthrough(self):
        assert _sanitize_csv_field(None) is None

    def test_empty_string_unchanged(self):
        assert _sanitize_csv_field("") == ""

    def test_value_preserved_after_prefix(self):
        result = _sanitize_csv_field("=MALICIOUS()")
        assert "=MALICIOUS()" in result


class TestCsvInjectionInLog:
    def _make_tracker(self, tmpdir: Path) -> GlobalImpactTracker:
        t = GlobalImpactTracker.__new__(GlobalImpactTracker)
        t.log_dir = tmpdir
        t.log_file = tmpdir / "test.csv"
        t.metrics_file = tmpdir / "metrics.json"
        t._ensure_log_exists()
        return t

    def test_formula_in_project_is_sanitized(self, tmp_path):
        t = self._make_tracker(tmp_path)
        t.log_impact("=MALICIOUS()", "task", 1.0, 60.0)
        with open(t.log_file) as f:
            rows = list(csv.DictReader(f))
        assert not rows[0]["Project"].startswith("=")

    def test_formula_in_task_is_sanitized(self, tmp_path):
        t = self._make_tracker(tmp_path)
        t.log_impact("project", "@CMD|' /C calc'!A0", 1.0, 60.0)
        with open(t.log_file) as f:
            rows = list(csv.DictReader(f))
        assert not rows[0]["Task"].startswith("@")

    def test_safe_values_written_unchanged(self, tmp_path):
        t = self._make_tracker(tmp_path)
        t.log_impact("my-project", "refactored auth module", 2.0, 120.0)
        with open(t.log_file) as f:
            rows = list(csv.DictReader(f))
        assert rows[0]["Project"] == "my-project"
        assert rows[0]["Task"] == "refactored auth module"
