import os
import sys
import tempfile
import hashlib
import pytest
from unittest.mock import MagicMock, patch

# Ensure project root is on sys.path for imports during tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import importlib.util

# Load download_model from the source file without importing package-level heavy deps
base_agents_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agents", "base_agents.py"))
spec = importlib.util.spec_from_file_location("base_agents", base_agents_path)
base_agents = importlib.util.module_from_spec(spec)
sys.modules["base_agents"] = base_agents
# Provide lightweight dummy modules for external dependencies used at module import time
import types
if "crewai" not in sys.modules:
    crewai_mod = types.ModuleType("crewai")
    class DummyAgent:
        def __init__(self, *args, **kwargs):
            pass
    crewai_mod.Agent = DummyAgent
    sys.modules["crewai"] = crewai_mod

if "langchain_community" not in sys.modules:
    lc_mod = types.ModuleType("langchain_community")
    sys.modules["langchain_community"] = lc_mod

if "langchain_community.llms" not in sys.modules:
    llms_mod = types.ModuleType("langchain_community.llms")
    class DummyLlama:
        def __init__(self, *args, **kwargs):
            pass
    llms_mod.LlamaCpp = DummyLlama
    sys.modules["langchain_community.llms"] = llms_mod

spec.loader.exec_module(base_agents)
download_model = base_agents.download_model


class DummyResponse:
    def __init__(self, chunks, headers=None):
        self._chunks = chunks
        self.headers = headers or {}

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=8192):
        for c in self._chunks:
            yield c

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@patch("requests.Session")
def test_download_success(mock_session_class):
    chunks = [b"abc", b"defg"]
    total = sum(len(c) for c in chunks)
    resp = DummyResponse(chunks, headers={"content-length": str(total)})

    mock_session = MagicMock()
    mock_session.get.return_value = resp
    mock_session_class.return_value = mock_session

    with tempfile.TemporaryDirectory() as td:
        dest = os.path.join(td, "model.bin")
        download_model("http://example.com/model", dest, model_sha256=None, progress=False)
        assert os.path.exists(dest)
        with open(dest, "rb") as f:
            data = f.read()
        assert data == b"".join(chunks)


@patch("requests.Session")
def test_download_checksum_mismatch(mock_session_class):
    chunks = [b"foo"]
    resp = DummyResponse(chunks, headers={"content-length": str(len(chunks[0]))})

    mock_session = MagicMock()
    mock_session.get.return_value = resp
    mock_session_class.return_value = mock_session

    with tempfile.TemporaryDirectory() as td:
        dest = os.path.join(td, "model.bin")
        wrong_sha = hashlib.sha256(b"bar").hexdigest()
        with pytest.raises(RuntimeError):
            download_model("http://example.com/model", dest, model_sha256=wrong_sha, progress=False)