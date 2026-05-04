# Validation

## 1. Fresh install from PyPI

- In a clean virtualenv with no prior state: `pip install global-impact-tracker`
- The canonical CLI command resolves and prints help with no import errors
- Log a task via CLI; confirm it writes to `~/.impact_tracker/global_productivity.csv`
- Confirm `__version__` matches the published PyPI version

## 2. README walkthrough

- A user with no prior context follows the public README top-to-bottom
- Free CLI section: install, first log, and first summary all succeed without consulting any other doc
- MCP access section: the Google Form link is present and live, the per-client config snippets are syntactically correct for each client, and the sample prompts are in a copy-pasteable format
- No broken links, no references to removed commands, no missing env var explanation

## 3. Both free and paid paths verified end-to-end

**Free CLI path:**
- Fresh `pip install` → log a task → run the dashboard summary → output is correct

**Paid MCP path (all four clients):**
- Claude Code: MCP server starts with a valid `IMPACT_TRACKER_LICENSE_KEY`; at
  least one sample prompt returns a non-error response
- Codex CLI: MCP config loads and the server is reachable; at least one tool
  call succeeds
- Gemini CLI: config loads and at least one tool call succeeds
- Windsurf: config loads and at least one tool call succeeds
- With an invalid or missing key, the server returns the expected Pro-gate error
  (not a crash)

## Definition of done

All three validation checks above pass, the Google Form URL is live and linked,
per-client config snippets have been manually tested in at least one client
(Claude Code is the primary), and the package is live on PyPI.
