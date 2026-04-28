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

# Run MCP server manually after installing the package
python3 mcp/server.py

# Run tests
.venv/bin/pytest tests/ -v
```

## Architecture

```
global_impact_tracker/
├── src/global_impact_tracker/  ← public package and CLI
├── core/                      ← compatibility shims during repo split
├── mcp/                       ← private MCP interface
├── tools/                     ← internal operator tooling
├── tests/          ← pytest test suite
├── pyproject.toml
└── requirements.txt
```

**Data flow:**
1. Public CLI calls or MCP tools use `global_impact_tracker.tracker.GlobalImpactTracker`
2. Logged data appends rows to `~/.impact_tracker/global_productivity.csv`
3. `get_metrics` / `get_dashboard_data` read from the same CSV
4. `generate_star_story` calls Gemini with live metrics (Pro tier)

**Runtime data (outside repo, never committed):**
- `~/.impact_tracker/global_productivity.csv` — master task log
- `~/.impact_tracker/metrics_snapshot.json` — latest snapshot

**Pro licensing:**
- Customer-facing env var: `IMPACT_TRACKER_LICENSE_KEY`
- Key format: `gip-{customer_id}-{expiry_yyyymmdd}-{64-char-hmac}`
- Developer-only key generation env var: `IMPACT_TRACKER_SIGNING_SECRET`
- `_SIGNING_KEY` in `global_impact_tracker.entitlements` must remain a placeholder in any public-facing commit and be replaced only in the private repo

## MCP Config

Windsurf config at `~/.codeium/windsurf/mcp_config.json`:
```json
{
  "mcpServers": {
    "global-impact-tracker": {
      "command": "/Users/elishebawiggins/projects/global_impact_tracker/.venv/bin/python",
      "args": ["/Users/elishebawiggins/projects/global_impact_tracker/mcp/server.py"],
      "env": {
        "GEMINI_API_KEY": "<key>",
        "IMPACT_TRACKER_LICENSE_KEY": "<gip-pro-key-if-applicable>"
      }
    }
  }
}
```
**Always use absolute paths — MCP clients use fork/exec, not a shell. `~` is not expanded.**
