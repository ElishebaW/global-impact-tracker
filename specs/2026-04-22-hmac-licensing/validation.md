# Validation

## Success criteria

The feature is ready to merge when HMAC licensing works for paid MCP access without relying on local key files, while preserving the local-first CLI model for free users.

## Required implementation outcomes

- `core/entitlements.py` verifies signed keys instead of checking a local file
- the accepted production key format is `gip-{customer_id}-{expiry_yyyymmdd}-{signature}`
- signatures use full HMAC-SHA256 output (64 lowercase hex chars)
- expired keys are rejected
- malformed keys are rejected safely
- `tools/generate_key.py` produces keys in the updated format that the verifier accepts
- paid MCP gating still flows through the shared `is_pro()` path
- no raw signing secret is committed; `_SIGNING_KEY` on the public branch is a placeholder
- `IMPACT_TRACKER_LICENSE_KEY` is the customer-facing env var; `STRIPE_LICENSE_KEY` is removed

## Automated validation

The following must pass before merge:

- unit tests for entitlement verification
- unit tests for expiry handling
- targeted integration coverage for the MCP paid path
- full regression suite for `tests/`

Minimum automated checks:

```bash
pytest tests/test_entitlements.py -v
pytest tests/ -v
```

If MCP integration tests live outside the main test file set, they must also be run and pass.

## Manual validation

Perform one manual end-to-end check:

1. Generate a key with `tools/generate_key.py`
2. Set `IMPACT_TRACKER_LICENSE_KEY` in the local MCP config
3. Exercise a paid MCP flow that depends on `is_pro()`
4. Confirm the paid flow succeeds with a valid unexpired key
5. Confirm the same flow fails with an expired or tampered key

## Review checklist

- verification logic uses `hmac.compare_digest`
- signature validation requires exactly 64 lowercase hex characters
- expiry parsing is strict and rejects invalid dates
- old file-based validation paths are removed
- old 3-part keys are rejected
- old `git-` prefix keys are rejected
- the generator and verifier use the same signed payload rules
- `_SIGNING_KEY` is a placeholder constant on the public branch
- `IMPACT_TRACKER_LICENSE_KEY` is used everywhere `STRIPE_LICENSE_KEY` was
- docs match the implemented key format and `gip-` prefix
- `CLAUDE.md` no longer references `valid_keys.txt`
- `tools/` handling is consistent with the planned repo split

## Merge blockers

Do not merge if any of the following are true:

- Pro access still depends on `~/.impact_tracker/valid_keys.txt`
- expiry is not enforced
- the generator output does not match the runtime verifier
- paid MCP behavior bypasses shared entitlement logic
- only narrow tests pass but the full suite regresses
- the implementation requires committing or exposing the raw signing secret
- `_SIGNING_KEY` contains the real production value on a public-facing branch
- `STRIPE_LICENSE_KEY` is still referenced in `core/entitlements.py`
- signatures shorter than 64 hex characters are accepted as valid
