import pytest
from unittest.mock import patch, AsyncMock
import httpx


MOCK_RESPONSE = {"candidates": [{"content": "ok"}]}


def _mock_post(return_value):
    mock = AsyncMock()
    mock.return_value = httpx.Response(200, json=return_value)
    return mock


@pytest.mark.parametrize("path", ["/gemini/v1/test", "/huggingface/models/test"])
def test_valid_bearer_token_passes(client, valid_headers, path):
    with patch("proxy.main.httpx.AsyncClient.post", _mock_post(MOCK_RESPONSE)):
        response = client.post(path, headers=valid_headers, json={})
    assert response.status_code == 200


@pytest.mark.parametrize("path", ["/gemini/v1/test", "/huggingface/models/test"])
def test_wrong_bearer_token_returns_403(client, path):
    response = client.post(path, headers={"Authorization": "Bearer wrong-token"}, json={})
    assert response.status_code == 403


@pytest.mark.parametrize("path", ["/gemini/v1/test", "/huggingface/models/test"])
def test_missing_auth_header_returns_403(client, path):
    response = client.post(path, json={})
    assert response.status_code == 403
