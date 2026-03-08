# Orchestration Insights

## Problem
Execution data usually lives in scattered notes, ticket comments, and memory. That makes it hard to prove how much time AI orchestration actually saves versus manual delivery.

## Solution
This tool creates a single live audit trail for impact:
- `tracker.py` logs each task with projected manual hours and actual AI runtime.
- `dashboard.py` converts that log into a live HTML dashboard.
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
- `tracker.py`: Core impact logging logic.
- `config.py`: Global settings.
- `dashboard.py`: Generates `live_impact_dashboard.html` from log data and STAR metrics.
- `requirements.txt`: Python dependencies.

## Run
```bash
cd /Users/elishebawiggins/projects/global_impact_tracker/orchestration_insights/app
python3 dashboard.py
```
Then open `live_impact_dashboard.html` in a browser.
