import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("HUGGINGFACE_API_KEY", "test-hf-key")
os.environ.setdefault("PROXY_BEARER_TOKEN", "test-bearer-token")

from proxy.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def valid_headers():
    return {"Authorization": "Bearer test-bearer-token"}
