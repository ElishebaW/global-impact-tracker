# Global Impact Tracker

Global Impact Tracker is a local-first Python package and CLI for proving the value of AI-assisted work. The public surface is the installable `global_impact_tracker` package. MCP server code and customer key issuance tooling remain non-public/operator-controlled surfaces.

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

## Private development surface

For the current transition state in this repo, a full local development environment can be installed with:

```bash
pip install -r requirements.txt
```

That installs the public package plus private-repo dependencies used here for MCP and test coverage.

Paid MCP behavior still requires:

- `GEMINI_API_KEY`
- `IMPACT_TRACKER_LICENSE_KEY`

Internal customer key issuance still requires:

- `IMPACT_TRACKER_SIGNING_SECRET`

## Licensing boundary

Paid MCP features use portable HMAC-signed license keys.

- Customer env var: `IMPACT_TRACKER_LICENSE_KEY`
- Key format: `gip-{customer_id}-{expiry_yyyymmdd}-{signature}`
- Internal signing env var: `IMPACT_TRACKER_SIGNING_SECRET`
- `_SIGNING_KEY` in the public package remains a placeholder in public-facing commits
