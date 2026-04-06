"""Global settings for the Global Impact Tracker."""

from pathlib import Path

# Location where the master CSV is saved.
MASTER_CSV_PATH = Path.home() / ".impact_tracker" / "global_productivity.csv"

# Canonical column order for the master CSV.
# All columns after Status are nullable — older rows that omit them parse cleanly
# because csv.DictReader returns None for missing keys.
CSV_COLUMNS = [
    "Date",
    "Project",
    "Task",
    "Human_Baseline_Hrs",
    "AI_Sec",
    "Status",
    "Task_Type",      # nullable str  — e.g. "feature", "bug", "refactor"
    "Complexity",     # nullable str  — e.g. "low", "medium", "high"
    "Tools_Used",     # nullable str  — pipe-separated, e.g. "claude|windsurf"
    "Dollars_Saved",  # nullable float — hours_saved * DEFAULT_HOURLY_RATE
    "Audience",       # nullable str  — "self", "manager", "recruiter"
    "Token_Usage",    # nullable int  — LLM tokens consumed for this task
]

# Hourly rate used to auto-compute Dollars_Saved when not provided directly.
# Derived from: $184,000 total annual comp (Glassdoor SWE benchmark)
# divided by 2,080 working hours/year (52 weeks × 40 hours) = $88.46/hr.
DEFAULT_HOURLY_RATE = 88.46
