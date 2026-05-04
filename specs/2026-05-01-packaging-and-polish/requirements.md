# Requirements

## Goal

Make Global Impact Tracker fully installable from pip and published to PyPI,
standardize documentation for free CLI users and paid MCP users (currently free
for a limited time), and provide clear MCP setup instructions for all supported
clients: Claude Code, Codex CLI, Gemini CLI, and Windsurf.

## Current State

- Public repo has a `pyproject.toml` but install ergonomics and entry point names
  have not been validated against a clean environment
- Not yet published to PyPI
- README has grown organically across phases and does not have a clean
  install-first structure for new users
- No clear CTA, key request flow, or per-client setup guide for the (currently
  free) paid MCP tier
- Naming may be inconsistent across commands, package names, and docs
- MCP config examples do not exist for Codex CLI, Gemini CLI, or Windsurf

## Decisions

- **Scope is the public repo for packaging and docs.** The private MCP repo gets
  updated paid-tier setup docs as part of this phase.
- **PyPI publishing is in scope.** The goal is a real `pip install
  global-impact-tracker` that works from PyPI, not just a local install.
- **MCP server is free for a limited time.** All docs describing the paid MCP
  tier should reflect this promotional stance and include a clear CTA so users
  know how to request access. No hard paywall language.
- **Key request flow is a Google Form.** Users who want MCP access submit a
  Google Form; a key is generated and emailed back to them. Docs must link to
  the form URL and describe the expected turnaround. The form URL will be added
  before the phase ships.
- **All four clients documented.** MCP install instructions must cover Claude
  Code, Codex CLI, Gemini CLI, and Windsurf — each with a working config
  snippet and any client-specific gotchas.
- **No new MCP tools.** This phase is packaging and docs only — no behavior
  changes to the MCP server or tracker model.
- **CSV schema unchanged.** Storage stays flat-file; this phase does not touch
  the tracker data model.
- **Naming decision locked in this phase.** Canonical CLI command name
  (`impact-tracker`, `git-impact`, etc.) confirmed and locked in
  `pyproject.toml` entry points.

## Out of Scope

- New MCP tools or behavior changes to the server
- Changes to CSV or decisions.jsonl schemas
- Landing page (Phase 8)
- Gemini proxy (Phase 7)
