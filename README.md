# Global Impact Tracker

Global Impact Tracker is a local-first Python package and CLI for proving the value of AI-assisted work. This repository is the public free-tier codebase.

## Public install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the public CLI entrypoints:

- `impact-tracker`
- `impact-dashboard`

You can also run the package directly:

```bash
python -m global_impact_tracker metrics
```

## Public CLI usage

Log a task:

```bash
impact-tracker log \
  --project "Project Name" \
  --task "Task description" \
  --baseline-hrs 2.5 \
  --ai-sec 45.2 \
  --status "Success"
```

Capture metrics:

```bash
impact-tracker metrics
```

Generate the dashboard HTML in the current directory:

```bash
impact-dashboard
```

## Public package boundary

The public package contains:

- shared tracker logic
- CSV-backed storage and metrics generation
- the placeholder entitlement verifier interface
- the CLI and dashboard entrypoints

The public package does not ship:

- the MCP server
- internal key issuance tooling
- any real signing secret

`core/` remains in the repo only as a compatibility shim over the installable package during the split.

## Private MCP companion repo

Paid MCP features, private entitlement verification, and internal customer key issuance live in the separate private repo:

- `global-impact-tracker-mcp`

That repo installs this public package as a dependency and should not be shipped in the public GitHub codebase.

## Licensing boundary

The public package keeps the entitlement interface so paid keys can still be validated by private code, but this repo does not ship the MCP server or internal operator tooling.

- Customer env var: `IMPACT_TRACKER_LICENSE_KEY`
- Key format: `gip-{customer_id}-{expiry_yyyymmdd}-{signature}`
- `_SIGNING_KEY` in the public package remains a placeholder in public-facing commits
