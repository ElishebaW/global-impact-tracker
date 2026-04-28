"""Global settings for the Global Impact Tracker."""

from pathlib import Path

MASTER_CSV_PATH = Path.home() / ".impact_tracker" / "global_productivity.csv"

CSV_COLUMNS = [
    "Date",
    "Project",
    "Task",
    "Human_Baseline_Hrs",
    "AI_Sec",
    "Status",
    "Task_Type",
    "Complexity",
    "Tools_Used",
    "Dollars_Saved",
    "Audience",
    "Token_Usage",
]

DEFAULT_HOURLY_RATE = 88.46
