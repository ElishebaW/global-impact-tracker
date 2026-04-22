# Roadmap

This roadmap reflects the current state of the project: core tracking, MCP integration, and reporting already exist. The next work should be split into very small phases, with licensing and repo separation first.

## Phase 1: HMAC licensing

- Replace file-based Pro checks with HMAC-signed keys
- Keep the public `is_pro()` interface stable
- Add focused tests for valid, invalid, malformed, and missing keys
- Verify paid MCP gating works with signed keys

## Phase 2: Key generation workflow

- Add a private key generation script
- Define the operational process for issuing keys
- Document required environment variables and local usage
- Ensure key creation never depends on committed secrets

## Phase 3: Repo split

- Move public tracking code into the public repo shape
- Isolate MCP server and key tooling into the private repo
- Update dependency lists for each repo
- Confirm the MCP server still loads shared core logic via configured path

## Phase 4: Expiring keys

- Extend the HMAC key format to include expiry
- Reject expired or malformed keys
- Add tests for expiry edge cases
- Document key migration from non-expiring format

## Phase 5: Reflection hardening

- Add validation and retry logic to Gemini estimation
- Add evaluator checks for STAR story accuracy against live metrics
- Keep generated narratives grounded in exact numbers
- Add integration coverage for reflection flows

## Phase 6: Reflection as tools

- Expose metrics summary and STAR story generation as tool-callable actions
- Allow agent workflows to chain metrics into narrative generation
- Preserve existing MCP behavior while enabling tool-based orchestration
- Add at least one end-to-end tool-call test

## Phase 7: Packaging and polish

- Package the CLI for pip installation
- Tighten installation and configuration docs
- Standardize local setup for free CLI users and paid MCP users
- Clean up naming and repo-level documentation after the split

## Sequencing rules

- Prefer the smallest change that reduces product risk first
- Finish licensing before repo split
- Finish repo split before broader product expansion
- Keep CSV as the storage layer until query pressure proves otherwise
