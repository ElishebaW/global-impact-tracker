# Plan

## 1. Replace file-based Pro validation

1. Inspect the current `core/entitlements.py` implementation and identify every file-based validation path.
2. Replace local-file key checks with HMAC verification helpers.
3. Preserve the public `is_pro()` call shape used by the rest of the codebase.
4. Switch verification to the 4-part expiring key format: `gip-{customer_id}-{expiry}-{signature}`.
5. Read the customer key from `IMPACT_TRACKER_LICENSE_KEY` instead of `STRIPE_LICENSE_KEY`.
6. Add the hardcoded `_SIGNING_KEY` constant; use a placeholder value on the public branch — the real value goes in the private repo only.

## 2. Implement expiry-aware verification

1. Parse `expiry` from `YYYYMMDD` into a date value.
2. Reject malformed dates and expired keys.
3. Compute the signed payload from `customer_id` and `expiry`.
4. Use constant-time comparison for signature validation.
5. Require the signature to be exactly 64 lowercase hex characters (full HMAC-SHA256 output).

## 3. Update the key generation workflow

`tools/generate_key.py` already exists but generates the old format (`git-` prefix, 16-char truncated signature, no expiry). Update it to:

1. Accept `customer_id` and `expiry` as inputs (replacing the current random `key_id` approach).
2. Read `IMPACT_TRACKER_SIGNING_SECRET` from the environment; its value must match `_SIGNING_KEY`.
3. Compute the signed payload as `{customer_id}-{expiry_yyyymmdd}`.
4. Emit full HMAC-SHA256 output (64 hex chars) formatted as `gip-{customer_id}-{expiry}-{signature}`.

## 4. Cover the core test matrix

1. Rewrite or replace entitlement tests that assume static keys or local files.
2. Add happy-path coverage for a valid, unexpired key.
3. Add failure-path coverage for:
   - tampered signature
   - tampered customer id
   - tampered expiry
   - malformed expiry
   - expired key
   - missing env var
   - empty env var
   - wrong prefix (including old `git-` prefix)
   - wrong segment count
   - empty key parts
   - old 3-part key format
   - signature not exactly 64 hex characters

## 5. Verify MCP gating still works

1. Confirm `mcp/server.py` continues to gate paid behavior through `is_pro()`.
2. Add or update a targeted integration test that exercises the paid path with a valid generated key.
3. Add a failure case showing the paid path is blocked for an invalid or expired key.

## 6. Prepare repo-split-safe docs and ignores

1. Keep `tools/` excluded from the public repo where appropriate.
2. Ensure `_SIGNING_KEY` is a placeholder in any public-facing commit.
3. Document the new key format, `gip-` prefix, and secret requirements.
4. Document `IMPACT_TRACKER_LICENSE_KEY` as the replacement for `STRIPE_LICENSE_KEY` in MCP config.
5. Update `CLAUDE.md` to remove the `valid_keys.txt` entry from the runtime data section.
6. Confirm the implementation is ready to move cleanly into the planned public/private repo split.

## 7. Run merge-readiness validation

1. Run the entitlement-focused tests first for fast feedback.
2. Run the full regression suite.
3. Perform a manual end-to-end check with a generated key against the paid flow.
4. Confirm no raw secret is committed anywhere in the repo.
5. Confirm `_SIGNING_KEY` is a placeholder on the current branch.

## 8. Trigger Phase 2: repo split

After this branch merges, immediately open Phase 2 (repo split). The MCP server must not be distributed to any customer until the private repo holds the real `_SIGNING_KEY` and the public repo holds only the placeholder. Do not defer this step.
