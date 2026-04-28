# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Commands

All commands run from the repo root (`/Users/elishebawiggins/projects/global_impact_tracker`):

```bash
# Install dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Log a task
impact-tracker log --project "Project Name" --task "Task description" --baseline-hrs 2.5 --ai-sec 45.2 --status "Success"

# Capture metrics snapshot
impact-tracker metrics

# Generate dashboard (writes live_impact_dashboard.html in cwd)
impact-dashboard

# Run tests
.venv/bin/pytest tests/ -v
```

## Architecture

```
global_impact_tracker/
├── src/global_impact_tracker/  ← public package and CLI
├── core/                      ← compatibility shims during repo split
├── tests/          ← pytest test suite
├── pyproject.toml
└── requirements.txt
```

**Data flow:**
1. Public CLI calls use `global_impact_tracker.tracker.GlobalImpactTracker`
2. Logged data appends rows to `~/.impact_tracker/global_productivity.csv`
3. `impact-dashboard` and metrics reads operate from the same CSV

**Runtime data (outside repo, never committed):**
- `~/.impact_tracker/global_productivity.csv` — master task log
- `~/.impact_tracker/metrics_snapshot.json` — latest snapshot

**Public licensing boundary:**
- Customer-facing env var: `IMPACT_TRACKER_LICENSE_KEY`
- Key format: `gip-{customer_id}-{expiry_yyyymmdd}-{64-char-hmac}`
- `_SIGNING_KEY` in `global_impact_tracker.entitlements` must remain a placeholder in any public-facing commit and be replaced only in the private repo
