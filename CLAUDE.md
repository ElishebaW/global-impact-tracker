# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Commands

All commands run from the repo root (`/Users/elishebawiggins/projects/global_impact_tracker`):

```bash
# Install dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Log a task
python3 core/tracker.py log --project "Project Name" --task "Task description" --baseline-hrs 2.5 --ai-sec 45.2 --status "Success"

# Capture metrics snapshot
python3 core/tracker.py metrics

# Generate dashboard (open core/live_impact_dashboard.html in browser after)
python3 core/dashboard.py

# Run MCP server manually (normally started by Windsurf)
python3 mcp/server.py

# Run tests
.venv/bin/pytest tests/ -v
```

## Architecture

```
global_impact_tracker/
├── core/           ← tracker engine (tracker.py, dashboard.py, config.py)
├── mcp/            ← MCP interface (server.py exposes 4 tools to Windsurf/Claude)
├── tests/          ← pytest test suite
└── requirements.txt
```

**Data flow:**
1. MCP client (Windsurf) calls `log_task` → `mcp/server.py` → `core/tracker.py` → appends row to `~/.impact_tracker/global_productivity.csv`
2. `get_metrics` / `get_dashboard_data` read from the same CSV
3. `generate_star_story` calls Gemini with live metrics (Pro tier)

**Runtime data (outside repo, never committed):**
- `~/.impact_tracker/global_productivity.csv` — master task log
- `~/.impact_tracker/metrics_snapshot.json` — latest snapshot

**Pro licensing:**
- Customer-facing env var: `IMPACT_TRACKER_LICENSE_KEY`
- Key format: `gip-{customer_id}-{expiry_yyyymmdd}-{64-char-hmac}`
- Developer-only key generation env var: `IMPACT_TRACKER_SIGNING_SECRET`
- `_SIGNING_KEY` in `core/entitlements.py` must remain a placeholder in any public-facing commit and be replaced only in the private repo

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
        "IMPACT_TRACKER_PATH": "/Users/elishebawiggins/projects/global_impact_tracker/core",
        "IMPACT_TRACKER_LICENSE_KEY": "<gip-pro-key-if-applicable>"
      }
    }
  }
}
```

**Always use absolute paths — MCP clients use fork/exec, not a shell. `~` is not expanded.**
