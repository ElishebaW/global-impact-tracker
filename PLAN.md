# Plan: HMAC Signed Keys + Repo Split

## Context

The current `is_pro()` checks `~/.impact_tracker/valid_keys.txt` on the local machine. Since the MCP server runs as a local process on each user's machine, external customers would never have that file — `is_pro()` would always return `False` for them. This plan replaces file-based validation with HMAC-signed keys that self-verify anywhere, then splits the repo so `core/` can be made public while `mcp/` stays private.

---

## Part 1: HMAC Signed Keys

### How it works

- Keys have format: `git-{key_id}-{signature}` where signature = `HMAC-SHA256(_SIGNING_SECRET, key_id)[:16]`
- `_SIGNING_SECRET` baked into `entitlements.py` is `SHA-256(raw_secret)` — one-way, so reading the source doesn't let you generate new keys
- Raw secret (`IMPACT_TRACKER_SIGNING_SECRET`) lives only in developer env var, never in any file

### Files to change

#### `core/entitlements.py` — full rewrite
- Remove `_VALID_KEYS` set and all file-based logic
- Remove `pathlib` import; add `hashlib`, `hmac`
- Add `_SIGNING_SECRET: bytes = hashlib.sha256(b"<raw_secret>").digest()` (hardcoded derived constant)
- Add `_KEY_PREFIX = "git-"`
- Add `_verify_key(key: str) -> bool`:
  - Split on `-`, expect exactly 3 parts: `["git", key_id, signature]`
  - Return `False` for wrong format, wrong prefix, empty parts
  - Re-derive `expected = hmac.new(_SIGNING_SECRET, key_id.encode(), "sha256").hexdigest()[:16]`
  - Return `hmac.compare_digest(signature, expected)`
- Rewrite `is_pro()` to: get env var → return `False` if empty → return `_verify_key(key)`
- Public `is_pro()` interface unchanged — `mcp/server.py` requires zero changes

#### `tools/generate_key.py` — new file (private repo only, never public)
- Reads `IMPACT_TRACKER_SIGNING_SECRET` env var (raises if missing)
- Derives signing secret: `hashlib.sha256(raw.encode()).digest()`
- Generates `key_id = secrets.token_hex(8)`
- Computes `sig = hmac.new(signing_secret, key_id.encode(), "sha256").hexdigest()[:16]`
- Prints `git-{key_id}-{sig}`

#### `.gitignore` — add `tools/` as safety net in public repo

### Tests

Rewrite `tests/test_entitlements.py` — delete `TestIsProStaticKeys` and `TestIsProFileKeys` entirely (no more static set, no more file).

New `TestIsProHMACVerification` with fixture:
```python
@pytest.fixture
def make_valid_key(monkeypatch):
    test_secret = hashlib.sha256(b"test-only-secret").digest()
    monkeypatch.setattr(entitlements, "_SIGNING_SECRET", test_secret)
    def _make(key_id: str = "abc12345") -> str:
        sig = hmac.new(test_secret, key_id.encode(), "sha256").hexdigest()[:16]
        return f"git-{key_id}-{sig}"
    return _make
```

Tests (12 total):
1. Valid key → True
2. Tampered signature → False
3. Tampered key_id → False
4. Wrong prefix (`pro-`) → False
5. Too few segments (`git-abc123`) → False
6. Too many segments (`git-a-b-c`) → False
7. Empty env var → False
8. Whitespace-only env var → False
9. Missing env var → False
10. Empty key_id (`git--somesig`) → False
11. Empty signature (`git-someid-`) → False
12. Random string with no dashes → False

No `importlib.reload()` needed — no module-level mutable state.

### Steps

1. Generate real `IMPACT_TRACKER_SIGNING_SECRET` locally
2. Derive and hardcode `_SIGNING_SECRET` constant in `entitlements.py`
3. Rewrite `core/entitlements.py`
4. Rewrite `tests/test_entitlements.py`
5. `pytest tests/test_entitlements.py -v` — must pass
6. `pytest tests/ -v` — must pass (regression)
7. Create `tools/generate_key.py` locally (not committed to public repo)
8. End-to-end test: generate key, set `STRIPE_LICENSE_KEY`, verify `is_pro()` → True

### PR

Open PR to `main` on `global-impact-tracker` with:
- `core/entitlements.py` rewrite
- `tests/test_entitlements.py` rewrite
- `.gitignore` update (`tools/`)

---

## Part 2: Repo Split (Option A — Two Repos)

**Public repo** (`global-impact-tracker`): `core/`, `tests/`, `README.md`, `CLAUDE.md`, `.gitignore`, root `requirements.txt` → slim to `pandas` + `matplotlib` only

**Private repo** (`global-impact-mcp`): `mcp/server.py`, `tools/generate_key.py`, `requirements.txt` (full: `mcp`, `google-genai`, `pandas`, `matplotlib`), `CLAUDE.md`, `.gitignore`

**Dev setup after split:**
- Clone both repos
- Private repo sets `IMPACT_TRACKER_PATH` to absolute path of `core/` in public clone — no code changes, server already uses this env var
- `IMPACT_TRACKER_SIGNING_SECRET` lives in developer shell env / `.env` (git-ignored)

### Steps

1. Create private `global-impact-mcp` repo on GitHub
2. Init locally with only `mcp/`, `tools/`, slim `requirements.txt`, `CLAUDE.md`, `.gitignore`
3. Update public repo: remove `mcp/` from tracking, slim `requirements.txt`, update `CLAUDE.md` (remove `valid_keys.txt` reference, note HMAC keys)
4. Add `tools/` to public `.gitignore`

### Tests

- `pytest tests/ -v` in public repo — must pass after `mcp/` is removed
- Smoke test MCP server in private repo: start `mcp/server.py`, verify it imports `core/` via `IMPACT_TRACKER_PATH`
- Verify MCP Gemini features work end-to-end in Windsurf with real Pro key

### PR

- Open PR to `main` on `global-impact-tracker`: slimmed `requirements.txt`, updated `CLAUDE.md`, `.gitignore` update
- Initial commit to `main` on `global-impact-mcp`: `mcp/server.py`, `tools/generate_key.py`, `requirements.txt`, `CLAUDE.md`
- File GitHub issue in `global-impact-mcp` for Gemini proxy (see Part 3 below)

---

## Part 3: Gemini Proxy Service (Future — post repo split)

**Goal:** Pro customers should not need to provide or pay for their own Gemini API key. The MCP server's `generate_star_story` tool makes Gemini calls; currently each customer must supply `GEMINI_API_KEY` in their MCP config and absorb any API costs. Since they're paying for the MCP server, we should cover Gemini call costs (Gemini Flash pricing is fractions of a cent per `generate_star_story` call).

**Architecture: FastAPI proxy**

- A small hosted service (Railway/Render/Fly.io) that holds our `GEMINI_API_KEY` server-side
- MCP server sends Gemini requests to the proxy instead of calling Google directly
- Proxy validates the customer's `STRIPE_LICENSE_KEY` on each request before forwarding to Gemini
- Returns Gemini response to MCP server transparently

**What changes:**
- `mcp/server.py` — `generate_star_story` calls proxy URL instead of `google.generativeai` directly
- New `PROXY_URL` env var in MCP config (replaces `GEMINI_API_KEY` for customers)
- `STRIPE_LICENSE_KEY` still passed by customer (proxy validates it server-side)
- New repo or subdirectory for the proxy service itself (FastAPI, one endpoint)
- `GEMINI_API_KEY` moves from customer MCP config to proxy server env

**What stays the same:**
- `is_pro()` gating in `mcp/server.py` — still blocks the tool call before hitting the proxy
- `STRIPE_LICENSE_KEY` env var — customer still sets this in their MCP config
- HMAC key format — proxy validates using the same `_verify_key()` logic

### Tests

- Unit tests for proxy: valid key → forwards to Gemini; invalid key → 401
- Integration test: MCP server calls proxy with valid key → returns story
- `pytest tests/ -v` in both repos after MCP server changes

### PR

- PR to `global-impact-mcp`: `mcp/server.py` changes to call proxy
- Separate repo/PR for the proxy service itself

### Issue to file in `global-impact-mcp` after repo split

Title: `feat: Gemini proxy service so customers don't need their own API key`

Body:
```
## Problem
Pro customers currently must supply GEMINI_API_KEY in their MCP config and absorb
Gemini API costs. Since they're paying for the MCP server, we should cover this.

## Solution
Build a small FastAPI proxy service that:
1. Accepts generate_star_story requests from the MCP server
2. Validates STRIPE_LICENSE_KEY (HMAC) on each request
3. Forwards to Gemini with our key
4. Returns the response

Customers remove GEMINI_API_KEY from their config; add PROXY_URL instead.

## Files to change
- mcp/server.py: call proxy instead of google.generativeai directly
- New proxy service (FastAPI, one endpoint, hosted on Railway/Render/Fly.io)
- README/setup docs: update customer MCP config instructions

## Notes
- Gemini Flash is ~$0.00015/1K tokens — very low cost per call
- Proxy doubles as server-side license validation (defense in depth)
- HMAC verification logic can be imported directly from core/entitlements.py
```

---

## Critical Files

- `core/entitlements.py` — full rewrite
- `tests/test_entitlements.py` — full rewrite
- `requirements.txt` — slim to pandas + matplotlib
- `CLAUDE.md` — update runtime data section
- `.gitignore` — add `tools/`
- `mcp/server.py` — no changes needed

## Verification Checklist

- [ ] Key from `generate_key.py` passes `is_pro()` on clean machine (no local files)
- [ ] Altering any character of a valid key → `False`
- [ ] `STRIPE_LICENSE_KEY` unset → `False`
- [ ] Old plain-string key format → `False`
- [ ] `pytest tests/ -v` all pass
- [ ] No test requires `IMPACT_TRACKER_SIGNING_SECRET` in env
- [ ] `git grep IMPACT_TRACKER_SIGNING_SECRET` finds nothing in public repo
- [ ] `tools/` in `.gitignore`
- [ ] MCP Gemini features work end-to-end in Windsurf
