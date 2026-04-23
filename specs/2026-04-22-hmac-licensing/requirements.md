# Requirements

## Feature

HMAC licensing for Pro access, including signed key validation, a private key generation workflow, expiry support, and end-to-end gating across `core` and `mcp`.

## Context

This feature consolidates roadmap phases 1 (HMAC licensing), 2 (key generation workflow), and 4 (expiring keys) into a single delivery. See [specs/roadmap.md](/Users/elishebawiggins/projects/global_impact_tracker/specs/roadmap.md).

It should follow the product constitution:

- [specs/mission.md](/Users/elishebawiggins/projects/global_impact_tracker/specs/mission.md): credibility matters, metrics and narratives must be grounded, and free CLI plus paid MCP should share one tracker model
- [specs/tech-stack.md](/Users/elishebawiggins/projects/global_impact_tracker/specs/tech-stack.md): Python for both CLI and MCP, local-first defaults, and clear separation between shared `core/` logic and paid `mcp/` features

The current file-based Pro check does not work for external MCP customers because it depends on local machine state that will not exist on customer machines.

## Scope

This feature spec includes all of the following:

- replace file-based `is_pro()` validation with HMAC-signed keys
- add a private key generation workflow
- add expiry support to keys
- define the end-to-end licensing flow across `core` and `mcp`

## Product requirements

- Free CLI usage must remain available without a Pro key
- Paid MCP features must rely on portable key verification instead of local files
- License checks must be deterministic and self-contained on the customer machine
- The public `is_pro()` interface should remain stable unless a breaking change is unavoidable
- Generated keys must be tamper-evident
- Expired keys must be rejected
- The design must support the planned public/private repo split

## Key format

The target key format is:

`gip-{customer_id}-{expiry_yyyymmdd}-{signature}`

The prefix `gip` stands for Global Impact Pro.

Example:

`gip-acme-20261231-a3f9c21b44e87d02c6e54f8a91b2d3e70f5c6a7b8d9e0f1a2b3c4d5e6f7a8b9`

The signature is the full HMAC-SHA256 output encoded as 64 lowercase hex characters, computed from the signed payload:

`{customer_id}-{expiry_yyyymmdd}`

The verification logic should:

- require exactly 4 segments
- require the `gip` prefix
- reject empty `customer_id`, `expiry`, or `signature`
- parse `expiry` as `YYYYMMDD`
- reject malformed dates
- reject expired keys
- recompute the HMAC and compare with `hmac.compare_digest`
- reject signatures that are not exactly 64 lowercase hex characters

## Secret handling

- Raw signing secret lives only in developer environment
- Key generation tooling must read the signing secret from `IMPACT_TRACKER_SIGNING_SECRET`
- No committed file may contain the raw secret in plaintext

## Signing key delivery

The verifier recomputes the HMAC at runtime and therefore needs the signing key available in the deployed code. Since the MCP server runs locally on customer machines, the signing key cannot live in customer-supplied configuration — a customer who can read their own MCP config could extract it and forge keys.

The resolved architecture:

- A constant `_SIGNING_KEY` is hardcoded in `core/entitlements.py` in the **private repo only**
- The public repo ships `entitlements.py` with a placeholder value for `_SIGNING_KEY` that causes all verification to fail
- `IMPACT_TRACKER_SIGNING_SECRET` is a developer-environment variable used by `tools/generate_key.py`; its value must match `_SIGNING_KEY`
- No customer-facing configuration needs to supply the signing secret

**The repo split is a prerequisite for safe customer-facing distribution.** This phase must be followed immediately by Phase 2 (repo split) before the MCP server is distributed to any customer. A real `_SIGNING_KEY` must not appear in any public-facing commit.

## Customer-facing environment variable

The customer provides their signed license key via `IMPACT_TRACKER_LICENSE_KEY` in their MCP server environment config. This replaces the old `STRIPE_LICENSE_KEY` name.

## File-level requirements

### `core/entitlements.py`

- remove file-based validation logic
- add HMAC verification helpers
- validate the new 4-part key format with expiry
- keep `is_pro()` as the stable entry point for callers
- read the customer key from `IMPACT_TRACKER_LICENSE_KEY` (replaces `STRIPE_LICENSE_KEY`)
- use the hardcoded `_SIGNING_KEY` constant for verification (not an env var)

### `tools/generate_key.py`

- exists only for private/developer use
- reads `IMPACT_TRACKER_SIGNING_SECRET` from the environment; its value must match `_SIGNING_KEY`
- requires `customer_id` and `expiry`
- prints a valid signed key in the production format

### `mcp/server.py`

- continue to rely on `is_pro()` for paid feature gating
- require no duplicate licensing logic unless there is a strong reason
- be covered by at least one end-to-end licensing check

### Documentation

- update developer-facing docs to explain the new key format and `gip-` prefix
- document `IMPACT_TRACKER_LICENSE_KEY` as the customer-facing env var
- document `IMPACT_TRACKER_SIGNING_SECRET` as the developer-only env var for key generation
- make the repo-split implication explicit: `_SIGNING_KEY` must not appear in any public-facing commit
- update `CLAUDE.md` to remove the `valid_keys.txt` reference from the runtime data section

## Out of scope

- hosted license validation
- Stripe or payment processing
- multi-tenant admin tooling
- Gemini proxy service
- SQLite migration

## Decisions

- HMAC is the v1 licensing mechanism
- expiry is included now, not deferred
- the generator workflow is part of this phase, not a later one
- end-to-end licensing coverage across `core` and `mcp` is part of merge readiness
- the signing key is hardcoded in the private repo, not supplied via customer config
- `STRIPE_LICENSE_KEY` is renamed to `IMPACT_TRACKER_LICENSE_KEY`
- the signature uses full HMAC-SHA256 output (64 lowercase hex chars), not a truncated form
- the key prefix is `gip-` (Global Impact Pro), not `git-`
