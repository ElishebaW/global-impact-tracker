from unittest.mock import AsyncMock, patch

import httpx
import pytest


HF_RESPONSE = [{"generated_text": "result"}]


@pytest.fixture
def mock_hf():
    mock = AsyncMock()
    mock.return_value = httpx.Response(200, json=HF_RESPONSE)
    return mock


def test_huggingface_forwards_body(client, valid_headers, mock_hf):
    with patch("proxy.main.httpx.AsyncClient.post", mock_hf):
        response = client.post("/huggingface/models/mistralai/Mistral-7B", headers=valid_headers, json={"inputs": "hello"})
    assert response.status_code == 200
    call_kwargs = mock_hf.call_args
    assert "api-inference.huggingface.co" in call_kwargs.args[0]


def test_huggingface_injects_api_key(client, valid_headers, mock_hf):
    with patch("proxy.main.httpx.AsyncClient.post", mock_hf):
        client.post("/huggingface/models/mistralai/Mistral-7B", headers=valid_headers, json={})
    forwarded_headers = mock_hf.call_args.kwargs.get("headers", {})
    assert forwarded_headers.get("Authorization") == "Bearer test-hf-key"


def test_huggingface_strips_bearer_token_from_proxy_auth(client, valid_headers, mock_hf):
    with patch("proxy.main.httpx.AsyncClient.post", mock_hf):
        client.post("/huggingface/models/mistralai/Mistral-7B", headers=valid_headers, json={})
    forwarded_headers = mock_hf.call_args.kwargs.get("headers", {})
    # proxy bearer token must not leak — only the HF API key goes upstream
    assert forwarded_headers.get("Authorization") == "Bearer test-hf-key"
    assert "test-bearer-token" not in str(forwarded_headers)
