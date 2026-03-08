# Orchestration Insights

## Why
I built this tool to quantify the transition from manual execution to AI orchestration. It serves as a real-time audit of my efficiency, proving a 90%+ reduction in task latency across multiple live projects.

## Live Impact Dashboard
This app can generate a visual dashboard with:
- A live `Total Hours Saved` ticker.
- A bar chart comparing `Projected Manual Hours` vs `Actual AI-Orchestrated Hours`.
- The project mission statement in a dedicated Why section.

## Files
- `tracker.py`: Core impact logging logic.
- `config.py`: Global settings.
- `dashboard.py`: Generates `live_impact_dashboard.html` from log data.
- `requirements.txt`: Python dependencies.

## Run
```bash
cd /Users/elishebawiggins/projects/global_impact_tracker/orchestration_insights/app
python3 dashboard.py
```
Open `live_impact_dashboard.html` in a browser.
