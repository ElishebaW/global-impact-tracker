# Validation

## 1. Proxy auth behavior

- Valid `PROXY_BEARER_TOKEN` → `200` on both `/gemini` and `/huggingface`
- Wrong bearer token → `403` with structured error body
- Missing `Authorization` header → `403`
- All three cases covered by automated tests that run without real API keys or secrets

## 2. Both upstream APIs reachable through the proxy

- `POST {PROXY_URL}/gemini` with a valid license key returns a real Gemini
  response (not a mock); confirm content is non-empty and status is `200`
- `POST {PROXY_URL}/huggingface` with a valid license key returns a real
  HuggingFace Inference API response; confirm status is `200`
- Neither call requires `GEMINI_API_KEY` or `HUGGINGFACE_API_KEY` in the
  calling environment

## 3. End-to-end MCP flow through the proxy

- Start the MCP server with `PROXY_URL` set and `GEMINI_API_KEY` /
  `HUGGINGFACE_API_KEY` unset
- From an MCP client (Claude Code), send a prompt that triggers STAR story
  generation; confirm a real story is returned with no errors
- Confirm the MCP server logs show requests going to `PROXY_URL`, not directly
  to Gemini

## 4. Invalid key rejected at the proxy layer

- Temporarily use an invalid license key in the MCP server config
- Confirm the MCP server receives a `403` from the proxy and surfaces a clear
  error to the client (not a crash or an unhandled exception)

## Definition of done

All four validation checks pass, both upstream APIs are confirmed reachable
through the deployed proxy, and customer docs no longer reference
`GEMINI_API_KEY` or `HUGGINGFACE_API_KEY`.
