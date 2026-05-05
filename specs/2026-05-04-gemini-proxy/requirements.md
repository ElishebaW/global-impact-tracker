# Requirements

## Goal

Build and deploy a small hosted proxy service that sits between the MCP server
and the Gemini and HuggingFace APIs. The proxy validates the customer's Pro
license key on every request and forwards valid requests to the appropriate
upstream API. Customers no longer need to supply `GEMINI_API_KEY` or
`HUGGINGFACE_API_KEY`; they only need `IMPACT_TRACKER_LICENSE_KEY` and a
`PROXY_URL`.

## Current state

- The MCP server calls the Gemini API directly using a customer-supplied
  `GEMINI_API_KEY`
- HuggingFace Inference API for LLM-as-judge evals also requires a
  customer-supplied `HUGGINGFACE_API_KEY`
- Key validation (HMAC) happens inside the MCP server process, not server-side
- Customers must manage two API keys in addition to their license key

## Decisions

- **Hosting: Google Cloud Run.** Serverless containers with scale-to-zero, close
  network proximity to the Gemini API, and straightforward secrets management
  via Google Secret Manager. The bearer token, Gemini key, and HuggingFace key
  all live in Secret Manager — never in source code or customer environments.
  The signing secret stays in the private MCP repo only.

- **Key validation: MCP server validates, proxy trusts via bearer token.** The
  MCP server runs `is_pro()` as it does today before calling the proxy. It then
  passes a shared `PROXY_BEARER_TOKEN` as an `Authorization: Bearer` header on
  every proxy request. The proxy checks only that the token matches the expected
  value from Secret Manager — it does not run HMAC logic and does not need the
  signing secret. The signing secret stays out of GCP entirely.

- **Phase scope: build + deploy to production.** Phase 8 is not complete until
  the proxy is live on Cloud Run and both a Gemini API call and a HuggingFace
  API call can be successfully made through the proxy with a valid license key.

- **Framework: FastAPI.** Small surface area, built-in async, automatic
  OpenAPI docs for debugging. Single-file service is sufficient for v1.

- **Two proxy endpoints.** `POST /gemini` forwards to the Gemini API;
  `POST /huggingface` forwards to the HuggingFace Inference API. Both require
  a valid `Authorization: Bearer` token. The proxy injects the upstream API key
  from Secret Manager before forwarding and strips the bearer token header.

- **MCP server change: `PROXY_URL` replaces direct API calls.** When
  `PROXY_URL` is set, the MCP server routes all Gemini and HuggingFace traffic
  through the proxy instead of calling upstream directly. `GEMINI_API_KEY` and
  `HUGGINGFACE_API_KEY` are no longer required in the customer environment.

- **Docs updated to reflect new customer setup.** README and MCP repo setup
  guide remove `GEMINI_API_KEY` and `HUGGINGFACE_API_KEY` from the customer
  env var table and replace them with `PROXY_URL`.

## Out of scope

- Multi-region deployment (single Cloud Run region for v1)
- Rate limiting or per-customer usage quotas
- Billing or usage metering
- Support for providers other than Gemini and HuggingFace
- Landing page (Phase 9)
