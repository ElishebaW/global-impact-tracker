"""Core tracking logic for orchestration insights."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path


class GlobalImpactTracker:
    def __init__(self):
        # Hidden home folder for persistent, cross-project tracking.
        self.log_dir = Path.home() / ".impact_tracker"
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "global_productivity.csv"
        self.metrics_file = self.log_dir / "metrics_snapshot.json"
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        if not self.log_file.exists():
            with open(self.log_file, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Date", "Project", "Task", "Human_Baseline_Hrs", "AI_Sec", "Status"])

    @staticmethod
    def _to_float(value: str | float | int | None) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    def _read_rows(self) -> list[dict[str, str]]:
        if not self.log_file.exists():
            return []
        with open(self.log_file, "r", newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def log_impact(self, project: str, task: str, baseline_hrs: float, ai_sec: float, status: str = "Success"):
        """Log one orchestrated task with explicit runtime."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        with open(self.log_file, "a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([timestamp, project, task, round(baseline_hrs, 4), round(ai_sec, 4), status])

    def get_total_savings(self) -> float:
        """Projected manual hours minus actual AI hours."""
        projected = 0.0
        actual = 0.0
        for row in self._read_rows():
            projected += self._to_float(row.get("Human_Baseline_Hrs"))
            actual += self._to_float(row.get("AI_Sec")) / 3600.0
        return round(max(projected - actual, 0.0), 4)

    def capture_metrics_snapshot(self) -> dict[str, float | int | str]:
        """
        Capture tracker-level operational metrics analogous to an API dashboard:
        - queries_processed: total logged orchestrations
        - avg_response_time_ms: average AI runtime per task in ms
        - system_health: derived from successful task ratio
        """
        rows = self._read_rows()
        queries_processed = len(rows)

        total_ai_sec = sum(self._to_float(r.get("AI_Sec")) for r in rows)
        avg_response_time_ms = ((total_ai_sec / queries_processed) * 1000.0) if queries_processed else 0.0

        success_count = sum(1 for r in rows if (r.get("Status") or "").strip().lower() == "success")
        failed_count = queries_processed - success_count
        success_rate_pct = ((success_count / queries_processed) * 100.0) if queries_processed else 0.0

        if success_rate_pct >= 95:
            system_health = "healthy"
        elif success_rate_pct >= 80:
            system_health = "degraded"
        else:
            system_health = "critical"

        unique_projects = len({(r.get("Project") or "Unknown").strip() for r in rows})
        projected_manual_hours = sum(self._to_float(r.get("Human_Baseline_Hrs")) for r in rows)
        ai_actual_hours = total_ai_sec / 3600.0
        total_hours_saved = max(projected_manual_hours - ai_actual_hours, 0.0)
        latency_reduction_pct = (
            (total_hours_saved / projected_manual_hours) * 100.0 if projected_manual_hours > 0 else 0.0
        )

        metrics = {
            "timestamp_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "queries_processed": queries_processed,
            "avg_response_time_ms": round(avg_response_time_ms, 2),
            "system_health": system_health,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate_pct": round(success_rate_pct, 2),
            "projects_count": unique_projects,
            "projected_manual_hours": round(projected_manual_hours, 4),
            "ai_actual_hours": round(ai_actual_hours, 4),
            "total_hours_saved": round(total_hours_saved, 4),
            "latency_reduction_pct": round(latency_reduction_pct, 2),
        }

        self.metrics_file.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        return metrics


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Global Impact Tracker CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    log_parser = subparsers.add_parser("log", help="Log one orchestration run")
    log_parser.add_argument("--project", required=True, help="Project name")
    log_parser.add_argument("--task", required=True, help="Task description")
    log_parser.add_argument("--baseline-hrs", type=float, required=True, help="Estimated manual hours")
    log_parser.add_argument("--ai-sec", type=float, required=True, help="Actual AI runtime in seconds")
    log_parser.add_argument("--status", default="Success", help="Run status (Success/Failed/etc.)")

    subparsers.add_parser("metrics", help="Capture and print JSON metrics snapshot")
    return parser


def main() -> None:
    tracker = GlobalImpactTracker()
    args = _build_cli().parse_args()

    if args.command == "log":
        tracker.log_impact(
            project=args.project,
            task=args.task,
            baseline_hrs=args.baseline_hrs,
            ai_sec=args.ai_sec,
            status=args.status,
        )
        print(f"Logged run to: {tracker.log_file}")
        return

    if args.command == "metrics":
        metrics = tracker.capture_metrics_snapshot()
        print(json.dumps(metrics, indent=2))
        print(f"Snapshot saved to: {tracker.metrics_file}")


if __name__ == "__main__":
    main()
