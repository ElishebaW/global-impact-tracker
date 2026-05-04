# Roadmap

This roadmap reflects the current state of the project: core tracking, MCP integration, and reporting already exist. The next work should be split into very small phases, with licensing and repo separation first.

## Phase 1: HMAC licensing (Complete)

Consolidates original phases 1 (HMAC licensing), 2 (key generation workflow), and 4 (expiring keys).

- Replace file-based Pro checks with HMAC-signed keys using the `gip-{customer_id}-{expiry}-{signature}` format
- Include expiry in the key format; reject expired and malformed keys
- Update `tools/generate_key.py` to the new format (customer_id, expiry, full 64-char HMAC output)
- Document `IMPACT_TRACKER_LICENSE_KEY` (customer) and `IMPACT_TRACKER_SIGNING_SECRET` (developer) env vars
- Keep the public `is_pro()` interface stable
- Add focused tests for valid, invalid, malformed, expired, and missing keys
- Verify paid MCP gating works with signed keys

## Phase 2: Repo split (Complete)

Must follow immediately after Phase 1 merges — do not ship the MCP server to customers before this is complete.

- Move public tracking code into the public repo shape
- Isolate MCP server, `tools/`, and the real `_SIGNING_KEY` constant into the private repo
- Public repo ships `entitlements.py` with only a placeholder `_SIGNING_KEY`
- Update dependency lists for each repo
- Confirm the MCP server still loads shared core logic via configured path

## Phase 3: Reflection hardening (Complete)

- Add validation and retry logic to Gemini estimation
- Add evaluator checks for STAR story accuracy against live metrics
- Keep generated narratives grounded in exact numbers
- Add integration coverage for reflection flows

## Phase 4: Decisions auto-capture (Complete)

- Investigate and fix Claude Code Stop hook not firing reliably (test with actual session exit, verify `transcript_path` is populated, confirm `ANTHROPIC_API_KEY` is available in hook subprocess environment)
- Harden `hooks/capture_decisions.py`: add stderr logging for silent failures so root cause is visible on next debug
- Validate end-to-end: hook fires → transcript read → Claude API called → `~/.impact_tracker/decisions.jsonl` written
- Surface captured decisions in `generate_star_story` (already wired in `_build_star_prompt`; confirm round-trip works with real data)
- Add a `get_decisions` MCP tool so decisions log is queryable directly from Claude Code

## Phase 5: Reflection as tools (Complete)

- Expose metrics summary and STAR story generation as tool-callable actions
- Add project-scoped STAR story generation so users can generate a narrative for one specific project instead of only a general cross-project story
- Allow agent workflows to chain metrics into narrative generation
- Preserve existing MCP behavior while enabling tool-based orchestration
- Add at least one end-to-end tool-call test
- Add LLM-as-judge qualitative eval: HuggingFace Inference API as primary critic, graceful degradation to a locally-run Ollama model (e.g., Llama 3 8B) on rate-limit errors
- Ollama is a required paid-tier install for the fallback eval path; document in paid-tier setup instructions

## Phase 6: Packaging and polish

- Package the CLI for pip installation
- Tighten installation and configuration docs
- Standardize local setup for free CLI users and paid MCP users
- Clean up naming and repo-level documentation after the split

## Phase 7: CI/CD pipeline

- Add a GitHub Actions workflow that runs on every pull request targeting `main` and every push to `main`:
  - Lint with `ruff` (style and import hygiene)
  - Format check with `ruff format --check`
  - Security scan with `bandit` (common Python security issues)
  - Dependency vulnerability scan with `pip-audit`
  - `pytest` across Python 3.11, 3.12, and 3.13
- Add a publish workflow triggered manually or on a tagged release (`v*`) that builds and uploads to PyPI
- Store `PYPI_API_TOKEN` as a GitHub Actions secret
- Add CI status and PyPI version badges to the README

## Phase 8: Gemini proxy service

- Move Gemini API usage for paid MCP features behind a small hosted proxy
- Validate Pro keys server-side before forwarding Gemini requests
- Remove the need for customers to supply their own `GEMINI_API_KEY`
- Add proxy unit tests and MCP-to-proxy integration coverage
- Also move `HUGGINGFACE_API_KEY` behind proxy for LLM-as-judge evaluations

Notes for this phase:

- This work happens after the repo split
- The proxy should preserve existing paid gating through shared entitlement logic
- A `PROXY_URL` should replace direct customer-side Gemini configuration for paid flows
- Proxy handles both Gemini API calls and HuggingFace API calls for evaluations

## Phase 9: Landing pages (free and paid tiers)

Build a product landing page for Global Impact Tracker modeled after codeguardian.studio — clean, developer-focused, with a clear free vs. paid tier split.

- Design a single-page site with hero, feature breakdown, free vs. paid comparison table, and a CTA for the paid MCP tier
- Free tier: highlight the CLI, CSV-based tracking, open-source availability
- Paid tier: highlight MCP server, AI estimation, STAR story generation, decisions capture, and team/enterprise positioning
- Include a live metrics demo section (animated or static sample numbers showing hours saved, latency reduction)
- Match the aesthetic of codeguardian.studio: minimal, dark or neutral palette, code-adjacent feel
- Host on the same domain pattern or a dedicated subdomain (e.g. globalimpacttracker.dev)
- Tie into the packaging phase — landing page goes live when pip install is ready

## Sequencing rules

- Prefer the smallest change that reduces product risk first
- Finish licensing before repo split
- Finish repo split before broader product expansion
- Keep CSV as the storage layer until query pressure proves otherwise
