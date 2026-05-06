from unittest.mock import AsyncMock, patch

import httpx
import pytest


GEMINI_RESPONSE = {"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]}


@pytest.fixture
def mock_gemini():
    mock = AsyncMock()
    mock.return_value = httpx.Response(200, json=GEMINI_RESPONSE)
    return mock


def test_gemini_forwards_body(client, valid_headers, mock_gemini):
    with patch("proxy.main.httpx.AsyncClient.post", mock_gemini):
        response = client.post("/gemini/v1beta/models/gemini-pro:generateContent", headers=valid_headers, json={"contents": [{"text": "hi"}]})
    assert response.status_code == 200
    call_kwargs = mock_gemini.call_args
    assert "generativelanguage.googleapis.com" in call_kwargs.args[0]


def test_gemini_injects_api_key(client, valid_headers, mock_gemini):
    with patch("proxy.main.httpx.AsyncClient.post", mock_gemini):
        client.post("/gemini/v1beta/models/gemini-pro:generateContent", headers=valid_headers, json={})
    params = mock_gemini.call_args.kwargs.get("params", {})
    assert params.get("key") == "test-gemini-key"


def test_gemini_strips_bearer_token(client, valid_headers, mock_gemini):
    with patch("proxy.main.httpx.AsyncClient.post", mock_gemini):
        client.post("/gemini/v1beta/models/gemini-pro:generateContent", headers=valid_headers, json={})
    forwarded_headers = mock_gemini.call_args.kwargs.get("headers", {})
    assert "Authorization" not in forwarded_headers
