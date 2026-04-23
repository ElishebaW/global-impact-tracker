# global-impact-mcp

MCP server that exposes the global_impact_tracker as callable tools for any MCP client (VS Code, JetBrains, Claude Desktop).

## Setup

```bash
cd ~/projects/global-impact-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## MCP Config

Add to your client's MCP config file:

```json
{
  "mcpServers": {
    "global-impact-tracker": {
      "command": "/Users/yourname/projects/global-impact-mcp/.venv/bin/python",
      "args": ["/Users/yourname/projects/global-impact-mcp/server.py"],
      "env": {
        "IMPACT_TRACKER_PATH": "<YOUR_TRACKER_PATH>",
        "GEMINI_API_KEY": "<YOUR_GEMINI_API_KEY>"
      }
    }
  }
}
```

> **Use absolute paths.** MCP clients invoke the command directly via `fork/exec` — `~` is not shell-expanded and will cause a "no such file or directory" error. Always use the full path (e.g. `/Users/yourname/...`).

**Config file locations:**
| Client | Config path |
|--------|-------------|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| VS Code | `.vscode/mcp.json` in workspace, or user settings |
| JetBrains | Settings → Tools → MCP Servers |

**Env vars:**
| Variable | Required | Description |
|----------|----------|-------------|
| `IMPACT_TRACKER_PATH` | Yes | Absolute path to `global_impact_tracker/orchestration_insights/app` |
| `GEMINI_API_KEY` | Recommended | Gemini API key for AI estimation. If omitted, `baseline_hours` and `ai_seconds` must be passed manually to `log_task`, and `generate_star_story` falls back to a template. |
| `IMPACT_TRACKER_LICENSE_KEY` | Optional | Signed Pro key for paid MCP flows, in the format `gip-{customer_id}-{expiry_yyyymmdd}-{64-char-hmac}`. |

## Pro Licensing

Paid MCP features use portable HMAC-signed license keys. Free CLI usage remains available without a Pro key.

- Customer-facing env var: `IMPACT_TRACKER_LICENSE_KEY`
- Production key format: `gip-{customer_id}-{expiry_yyyymmdd}-{signature}`
- Signature format: full HMAC-SHA256 output as 64 lowercase hex characters
- Developer-only env var for private key generation: `IMPACT_TRACKER_SIGNING_SECRET`
- Repo split requirement: `_SIGNING_KEY` in `core/entitlements.py` must stay a placeholder in any public-facing commit; the real value belongs only in the private repo

## Tools

### `log_task`
Log a completed task. Gemini estimates `baseline_hours` and `ai_seconds` from context — you don't supply them manually.

```
project      — project name
task         — what was done
context      — what Claude knows: files touched, complexity, time elapsed
status       — "Success" (default) or "Failed"
baseline_hours  — optional override
ai_seconds      — optional override
```

### `get_metrics`
Returns the current STAR metrics snapshot (total tasks, hours saved, latency reduction, system health).

### `get_dashboard_data`
Returns aggregated stats per project — tasks, baseline hours, AI hours, hours saved, latency reduction %.

### `generate_star_story`
Calls Gemini with live metrics data to produce a STAR narrative for performance reviews or self-assessments.

## Workflow

Claude (or any MCP client) handles estimation automatically:

> "Log that refactor I just did on the auth module"

Claude calls `log_task` with the task description and context it already has from the conversation. Gemini estimates the time values. No manual number entry.

> "Give me my STAR story for my self-review"

Claude calls `generate_star_story` — Gemini narrates your own productivity impact using real tracked data.
