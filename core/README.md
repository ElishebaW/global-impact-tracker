# Core Compatibility Layer

`core/` is now a compatibility shim over the installable `global_impact_tracker` package. The public/shared implementation lives under `src/global_impact_tracker/`.

## Problem
Execution data usually lives in scattered notes, ticket comments, and memory. That makes it hard to prove how much time AI orchestration actually saves versus manual delivery.

## Solution
This tool creates a single live audit trail for impact:
- `global_impact_tracker.tracker` logs each task with projected manual hours and actual AI runtime.
- `global_impact_tracker.dashboard` converts that log into a live HTML dashboard.
- `live_impact_dashboard.html` shows a bar chart, live savings ticker, and STAR-ready metrics.

## STAR Story Metrics Provided
The dashboard produces metrics mapped to STAR language so you can reuse them in interviews, performance reviews, and case studies.

- `Situation`: number of active projects and tracked tasks.
- `Task`: total projected manual hours.
- `Action`: total actual AI-orchestrated hours.
- `Result`: total hours saved and latency-reduction percentage.

The `STAR Story Metrics` panel and narrative are generated from your latest log data every time you run the script.

## Why
I built this tool to quantify the transition from manual execution to AI orchestration. It serves as a real-time audit of my efficiency, proving a 90%+ reduction in task latency across multiple live projects.

## Files
- `tracker.py`: Compatibility wrapper for the public package tracker CLI/module.
- `config.py`: Compatibility wrapper for public package settings.
- `dashboard.py`: Compatibility wrapper for dashboard generation.
- `entitlements.py`: Compatibility wrapper for the placeholder public entitlement interface.

## Configuration Settings

The tracker uses the following configuration in `config.py`:

- `MASTER_CSV_PATH`: Location where the master CSV log is saved. Defaults to `data/master_tracker.csv` relative to the app directory.

The GlobalImpactTracker class automatically creates a hidden directory in your home folder (`~/.impact_tracker/`) for persistent, cross-project tracking. This contains:
- `global_productivity.csv`: Main log file with all tracked tasks
- `metrics_snapshot.json`: Latest metrics snapshot

## Logging Usage

### Command Line Interface

Use the installed CLI to log orchestration runs:

#### Log a Task
```bash
impact-tracker log --project "Project Name" --task "Task description" --baseline-hrs 2.5 --ai-sec 45.2 --status "Success"
```

**Parameters:**
- `--project`: Name of the project (required)
- `--task`: Description of the task performed (required)  
- `--baseline-hrs`: Estimated manual hours this task would have taken (required, float)
- `--ai-sec`: Actual AI runtime in seconds (required, float)
- `--status`: Run status - defaults to "Success" (optional, string)

#### Capture Metrics Snapshot
```bash
impact-tracker metrics
```
This captures current metrics and saves them to `~/.impact_tracker/metrics_snapshot.json`.

### Logging Examples

```bash
# Log a successful API integration task
impact-tracker log --project "E-commerce Site" --task "REST API integration" --baseline-hrs 4.0 --ai-sec 120.5

# Log a failed database migration
impact-tracker log --project "Data Pipeline" --task "Database migration" --baseline-hrs 2.0 --ai-sec 30.0 --status "Failed"

# Log quick code generation
impact-tracker log --project "Mobile App" --task "Generate React components" --baseline-hrs 1.5 --ai-sec 15.2
```

### Metrics Interpretation

The metrics snapshot provides the following key metrics:

- **queries_processed**: Total number of logged orchestration tasks
- **avg_response_time_ms**: Average AI runtime per task in milliseconds
- **system_health**: Overall system health based on success rate:
  - "healthy": ≥95% success rate
  - "degraded": 80-94% success rate  
  - "critical": <80% success rate
- **success_rate_pct**: Percentage of successful tasks
- **projects_count**: Number of unique projects tracked
- **projected_manual_hours**: Total estimated manual hours for all tasks
- **ai_actual_hours**: Total actual AI hours spent
- **total_hours_saved**: Hours saved (projected - actual)
- **latency_reduction_pct**: Percentage reduction in task completion time

## Run
```bash
impact-dashboard
```
Then open `live_impact_dashboard.html` in a browser.
