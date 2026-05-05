# Task Groups

## 1. Build the proxy service

Create `proxy/main.py` — a FastAPI app with two endpoints:

- `POST /gemini` — checks `Authorization: Bearer` header against
  `PROXY_BEARER_TOKEN` from env, then forwards the request body to the Gemini
  API using `GEMINI_API_KEY` from Secret Manager
- `POST /huggingface` — same bearer check, forwards to the HuggingFace
  Inference API using `HUGGINGFACE_API_KEY` from Secret Manager
- Both endpoints return the upstream response body and status code directly
- On missing/invalid bearer token: return `403` with `{"error": "unauthorized"}`
- `PROXY_BEARER_TOKEN`, `GEMINI_API_KEY`, and `HUGGINGFACE_API_KEY` are all
  read from env (mounted from Secret Manager at deploy time)

Create `proxy/requirements.txt`:
```
fastapi
uvicorn[standard]
httpx
```

## 2. Write proxy tests

Create `proxy/tests/`:

- `test_auth.py` — valid bearer token passes both endpoints; wrong token
  returns 403; missing `Authorization` header returns 403
- `test_gemini_endpoint.py` — mock upstream Gemini response with
  `httpx.MockTransport`; confirm proxy forwards body, injects `GEMINI_API_KEY`,
  and strips the bearer token before sending upstream
- `test_huggingface_endpoint.py` — same pattern for HuggingFace endpoint
- All tests run without real API keys or a real signing secret

## 3. Containerize

Create `proxy/Dockerfile`:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Create `proxy/.dockerignore` to exclude `__pycache__/`, `tests/`, `.env`.

Verify locally: `docker build -t impact-tracker-proxy proxy/` runs cleanly.

## 4. Set up GCP infrastructure

Document in `proxy/DEPLOY.md`:

1. Enable APIs: Cloud Run, Artifact Registry, Secret Manager
2. Create secrets in Secret Manager:
   - `PROXY_BEARER_TOKEN` (generate a strong random value; also set this in the MCP server deployment)
   - `GEMINI_API_KEY`
   - `HUGGINGFACE_API_KEY`
3. Create a service account with `secretmanager.secretAccessor` role
4. Build and push container to Artifact Registry:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/impact-tracker-proxy proxy/
   ```
5. Deploy to Cloud Run with secrets mounted as env vars:
   ```bash
   gcloud run deploy impact-tracker-proxy \
     --image gcr.io/PROJECT_ID/impact-tracker-proxy \
     --set-secrets PROXY_BEARER_TOKEN=PROXY_BEARER_TOKEN:latest \
     --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest \
     --set-secrets HUGGINGFACE_API_KEY=HUGGINGFACE_API_KEY:latest \
     --allow-unauthenticated \
     --region us-central1
   ```

## 5. Smoke-test deployed proxy

- Send a `POST /gemini` request with a valid license key; confirm a real Gemini
  response is returned
- Send a `POST /huggingface` request with a valid license key; confirm a real
  HuggingFace response is returned
- Send a request with an invalid key to each endpoint; confirm `403` is returned

## 6. Update MCP server to use PROXY_URL

In the private `global-impact-tracker-mcp` repo:

- MCP server already validates `IMPACT_TRACKER_LICENSE_KEY` via `is_pro()`
  before any API call — no change needed there
- When `PROXY_URL` is set, route all Gemini calls to `{PROXY_URL}/gemini` and
  HuggingFace calls to `{PROXY_URL}/huggingface`, passing `PROXY_BEARER_TOKEN`
  as `Authorization: Bearer` header
- Keep the existing direct-call path as a fallback when `PROXY_URL` is not set
  (supports local dev without the proxy running)
- Remove `GEMINI_API_KEY` and `HUGGINGFACE_API_KEY` from required customer env vars
- `PROXY_BEARER_TOKEN` is an operator env var on the MCP server deployment — not exposed to customers

## 7. Update customer-facing docs

- Remove `GEMINI_API_KEY` and `HUGGINGFACE_API_KEY` from the public README env
  var table
- Add `PROXY_URL` to the env var table
- Update all four client config snippets (Claude Code, Codex, Gemini CLI,
  Windsurf) to remove the now-unnecessary API key env vars
- Update the MCP repo setup guide accordingly
