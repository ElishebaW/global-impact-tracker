# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `orchestration_insights/app/`:

```bash
# Install dependencies
pip install -r requirements.txt

# Log a task
python3 tracker.py log --project "Project Name" --task "Task description" --baseline-hrs 2.5 --ai-sec 45.2 --status "Success"

# Capture metrics snapshot
python3 tracker.py metrics

# Generate dashboard (open live_impact_dashboard.html in browser after)
python3 dashboard.py
```

## Architecture

This tool quantifies the productivity impact of AI orchestration by comparing projected manual hours vs. actual AI execution time.

**Data flow:**
1. `tracker.py log` → appends a row to `~/.impact_tracker/global_productivity.csv`
2. `dashboard.py` reads that CSV → aggregates by project → writes `live_impact_dashboard.html`

**Key components:**

- **tracker.py** — `GlobalImpactTracker` class manages the persistent CSV log at `~/.impact_tracker/`. Exposes a CLI with two subcommands: `log` and `metrics`. The `capture_metrics_snapshot()` method derives system health, success rate, and latency reduction from the CSV and writes to `~/.impact_tracker/metrics_snapshot.json`.

- **dashboard.py** — Reads the CSV, aggregates manual vs. AI hours per project, then generates a self-contained HTML file with Chart.js visualizations. The STAR narrative (Situation/Task/Action/Result) is auto-generated from live metrics.

- **config.py** — Defines `MASTER_CSV_PATH`, though `tracker.py` currently uses `~/.impact_tracker/` directly (config path is not yet wired in).

- **live_impact_dashboard.html** — Generated output; not hand-edited.

**Runtime data (outside repo):**
- `~/.impact_tracker/global_productivity.csv` — master task log
- `~/.impact_tracker/metrics_snapshot.json` — latest snapshot
