"""Core tracking logic for Global Impact Tracker."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime

from .config import CSV_COLUMNS, DEFAULT_HOURLY_RATE, MASTER_CSV_PATH

_FORMULA_PREFIXES = frozenset("=+-@\t\r\n＝＋－＠")


def _sanitize_csv_field(value: str | None) -> str | None:
    """Prefix formula-triggering characters to prevent CSV injection."""
    return (
        ("\t" + value)
        if (isinstance(value, str) and value and value[0] in _FORMULA_PREFIXES)
        else value
    )


class GlobalImpactTracker:
    def __init__(self):
        self.log_file = MASTER_CSV_PATH
        self.log_dir = self.log_file.parent
        self.log_dir.mkdir(exist_ok=True)
        self.metrics_file = self.log_dir / "metrics_snapshot.json"
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        if not self.log_file.exists():
            with open(self.log_file, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(CSV_COLUMNS)

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

    def log_impact(
        self,
        project: str,
        task: str,
        baseline_hrs: float,
        ai_sec: float,
        status: str = "Success",
        *,
        task_type: str | None = None,
        complexity: str | None = None,
        tools_used: str | None = None,
        dollars_saved: float | None = None,
        audience: str | None = None,
        token_usage: int | None = None,
    ) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d")

        if dollars_saved is None:
            hours_saved = max(baseline_hrs - (ai_sec / 3600.0), 0.0)
            dollars_saved = round(hours_saved * DEFAULT_HOURLY_RATE, 2)

        with open(self.log_file, "a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    timestamp,
                    _sanitize_csv_field(project),
                    _sanitize_csv_field(task),
                    round(baseline_hrs, 4),
                    round(ai_sec, 4),
                    _sanitize_csv_field(status),
                    _sanitize_csv_field(task_type),
                    _sanitize_csv_field(complexity),
                    _sanitize_csv_field(tools_used),
                    dollars_saved,
                    _sanitize_csv_field(audience),
                    token_usage,
                ]
            )

    def get_total_savings(self) -> float:
        projected = 0.0
        actual = 0.0
        for row in self._read_rows():
            projected += self._to_float(row.get("Human_Baseline_Hrs"))
            actual += self._to_float(row.get("AI_Sec")) / 3600.0
        return round(max(projected - actual, 0.0), 4)

    def capture_metrics_snapshot(self) -> dict[str, float | int | str]:
        rows = self._read_rows()
        queries_processed = len(rows)

        total_ai_sec = sum(self._to_float(r.get("AI_Sec")) for r in rows)
        avg_response_time_ms = (
            ((total_ai_sec / queries_processed) * 1000.0) if queries_processed else 0.0
        )

        success_count = sum(
            1 for r in rows if (r.get("Status") or "").strip().lower() == "success"
        )
        failed_count = queries_processed - success_count
        success_rate_pct = (
            ((success_count / queries_processed) * 100.0) if queries_processed else 0.0
        )

        if success_rate_pct >= 95:
            system_health = "healthy"
        elif success_rate_pct >= 80:
            system_health = "degraded"
        else:
            system_health = "critical"

        unique_projects = len({(r.get("Project") or "Unknown").strip() for r in rows})
        projected_manual_hours = sum(
            self._to_float(r.get("Human_Baseline_Hrs")) for r in rows
        )
        ai_actual_hours = total_ai_sec / 3600.0
        total_hours_saved = max(projected_manual_hours - ai_actual_hours, 0.0)
        latency_reduction_pct = (
            (total_hours_saved / projected_manual_hours) * 100.0
            if projected_manual_hours > 0
            else 0.0
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
    log_parser.add_argument("--project", required=True)
    log_parser.add_argument("--task", required=True)
    log_parser.add_argument("--baseline-hrs", type=float, required=True)
    log_parser.add_argument("--ai-sec", type=float, required=True)
    log_parser.add_argument("--status", default="Success")
    log_parser.add_argument(
        "--task-type", default=None, help="feature | bug | refactor | review"
    )
    log_parser.add_argument("--complexity", default=None, help="low | medium | high")
    log_parser.add_argument(
        "--tools-used", default=None, help="Pipe-separated: claude|windsurf|gemini"
    )
    log_parser.add_argument(
        "--dollars-saved", type=float, default=None, help="Override auto-computed value"
    )
    log_parser.add_argument(
        "--audience", default=None, help="self | manager | recruiter"
    )
    log_parser.add_argument(
        "--token-usage", type=int, default=None, help="LLM tokens consumed"
    )

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
            task_type=args.task_type,
            complexity=args.complexity,
            tools_used=args.tools_used,
            dollars_saved=args.dollars_saved,
            audience=args.audience,
            token_usage=args.token_usage,
        )
        print(f"Logged run to: {tracker.log_file}")
        return

    if args.command == "metrics":
        metrics = tracker.capture_metrics_snapshot()
        print(json.dumps(metrics, indent=2))
        print(f"Snapshot saved to: {tracker.metrics_file}")
