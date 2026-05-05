from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
HUGGINGFACE_API_KEY = os.environ["HUGGINGFACE_API_KEY"]
PROXY_BEARER_TOKEN = os.environ["PROXY_BEARER_TOKEN"]

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com"
HUGGINGFACE_BASE_URL = "https://api-inference.huggingface.co"

app = FastAPI()
_bearer = HTTPBearer(auto_error=False)


def _verify_token(credentials: HTTPAuthorizationCredentials | None = Security(_bearer)) -> None:
    if credentials is None or credentials.credentials != PROXY_BEARER_TOKEN:
        raise HTTPException(status_code=403, detail="unauthorized")


@app.post("/gemini/{path:path}")
async def proxy_gemini(path: str, request: Request, credentials: HTTPAuthorizationCredentials = Security(_bearer)):
    _verify_token(credentials)
    body = await request.body()
    params = dict(request.query_params)
    params["key"] = GEMINI_API_KEY
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GEMINI_BASE_URL}/{path}",
            content=body,
            params=params,
            headers={"Content-Type": request.headers.get("Content-Type", "application/json")},
        )
    return response.json()


@app.post("/huggingface/{path:path}")
async def proxy_huggingface(path: str, request: Request, credentials: HTTPAuthorizationCredentials = Security(_bearer)):
    _verify_token(credentials)
    body = await request.body()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{HUGGINGFACE_BASE_URL}/{path}",
            content=body,
            headers={
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": request.headers.get("Content-Type", "application/json"),
            },
        )
    return response.json()
