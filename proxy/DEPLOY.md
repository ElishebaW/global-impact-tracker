# Deploying the Gemini Proxy to Cloud Run

## Prerequisites

- Google Cloud project with billing enabled
- `gcloud` CLI authenticated (`gcloud auth login`)
- Docker installed locally

## 1. Enable GCP APIs

```bash
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

## 2. Create secrets in Secret Manager

```bash
echo -n "your-random-bearer-token" | gcloud secrets create PROXY_BEARER_TOKEN --data-file=-
echo -n "your-gemini-api-key"      | gcloud secrets create GEMINI_API_KEY --data-file=-
echo -n "your-huggingface-api-key" | gcloud secrets create HUGGINGFACE_API_KEY --data-file=-
```

Generate a strong bearer token (share this with the MCP server operator only):
```bash
openssl rand -hex 32
```

## 3. Create a service account

```bash
gcloud iam service-accounts create impact-tracker-proxy \
  --display-name "Impact Tracker Proxy"

gcloud secrets add-iam-policy-binding PROXY_BEARER_TOKEN \
  --member "serviceAccount:impact-tracker-proxy@PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member "serviceAccount:impact-tracker-proxy@PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding HUGGINGFACE_API_KEY \
  --member "serviceAccount:impact-tracker-proxy@PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/secretmanager.secretAccessor"
```

## 4. Build and push the container

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

gcloud artifacts repositories create impact-tracker \
  --repository-format=docker \
  --location=$REGION

gcloud builds submit \
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/impact-tracker/proxy \
  proxy/
```

## 5. Deploy to Cloud Run

```bash
gcloud run deploy impact-tracker-proxy \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/impact-tracker/proxy \
  --service-account impact-tracker-proxy@$PROJECT_ID.iam.gserviceaccount.com \
  --set-secrets PROXY_BEARER_TOKEN=PROXY_BEARER_TOKEN:latest \
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --set-secrets HUGGINGFACE_API_KEY=HUGGINGFACE_API_KEY:latest \
  --allow-unauthenticated \
  --region $REGION
```

The deploy command prints the service URL. Set this as `PROXY_URL` in the MCP
server deployment.

## 6. Smoke test

```bash
export PROXY_URL=https://your-service-url.run.app
export LICENSE_KEY=gip-your-key-here
export BEARER=your-random-bearer-token

# Gemini
curl -s -X POST "$PROXY_URL/gemini/v1beta/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $BEARER" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Say hello"}]}]}' | jq .

# HuggingFace
curl -s -X POST "$PROXY_URL/huggingface/models/mistralai/Mistral-7B-Instruct-v0.3" \
  -H "Authorization: Bearer $BEARER" \
  -H "Content-Type: application/json" \
  -d '{"inputs":"Hello"}' | jq .
```

## MCP server configuration

Set these in the MCP server deployment (not exposed to customers):

| Variable | Value |
|---|---|
| `PROXY_URL` | Cloud Run service URL |
| `PROXY_BEARER_TOKEN` | The bearer token from Secret Manager |

Remove `GEMINI_API_KEY` and `HUGGINGFACE_API_KEY` from the MCP server env.
