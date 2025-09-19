import os
import tempfile
import shutil
import json
import importlib
import sys
import pytest


@pytest.fixture(autouse=True)
def no_auto_download_env(monkeypatch):
    # Prevent model auto download during tests
    monkeypatch.setenv("MODEL_AUTO_DOWNLOAD", "false")
    yield


def test_match_jobs_loads_index_without_model(monkeypatch, tmp_path):
    # Create minimal FAISS index directory expected by match_jobs
    email = "test@example.com"
    user_dir = tmp_path / "faiss_index" / email
    user_dir.mkdir(parents=True)

    # Create a dummy "default__vector_store.json" file to satisfy existence check
    (user_dir / "default__vector_store.json").write_text(json.dumps({"dummy": True}))

    # Monkeypatch the persist directory location used by the function
    # The module under test references f"faiss_index/{email}", so we ensure CWD contains our tmp faiss_index
    monkeypatch.chdir(str(tmp_path))

    # Create lightweight stubs for the external `llama_index` package so importing
    # `backend.app.job_matcher` does not require the real dependency.
    import types

    llama_pkg = types.ModuleType("llama_index")
    embeddings_pkg = types.ModuleType("llama_index.embeddings")
    fastembed_mod = types.ModuleType("llama_index.embeddings.fastembed")

    class FastEmbedEmbedding:
        def __init__(self, *args, **kwargs):
            pass

    fastembed_mod.FastEmbedEmbedding = FastEmbedEmbedding
    embeddings_pkg.fastembed = fastembed_mod

    core_mod = types.ModuleType("llama_index.core")

    class Settings:
        embed_model = None
        llm = None

    core_mod.Settings = Settings

    class StorageContext:
        @staticmethod
        def from_defaults(persist_dir=None):
            return object()

    core_mod.StorageContext = StorageContext
    # placeholder; will be monkeypatched later
    core_mod.load_index_from_storage = lambda storage_context: None

    llms_mod = types.ModuleType("llama_index.llms")
    llama_cpp_mod = types.ModuleType("llama_index.llms.llama_cpp")

    class LlamaCPPPlaceholder:
        def __init__(self, *args, **kwargs):
            pass

    llama_cpp_mod.LlamaCPP = LlamaCPPPlaceholder
    llms_mod.llama_cpp = llama_cpp_mod

    # Insert stubs into sys.modules so normal imports succeed
    sys.modules["llama_index"] = llama_pkg
    sys.modules["llama_index.embeddings"] = embeddings_pkg
    sys.modules["llama_index.embeddings.fastembed"] = fastembed_mod
    sys.modules["llama_index.core"] = core_mod
    sys.modules["llama_index.llms"] = llms_mod
    sys.modules["llama_index.llms.llama_cpp"] = llama_cpp_mod

    # Stub pymongo and gridfs so job_matcher can import without those packages
    pymongo_mod = types.ModuleType("pymongo")
    class MongoClientStub:
        def __init__(self, *args, **kwargs):
            pass

    pymongo_mod.MongoClient = MongoClientStub
    sys.modules["pymongo"] = pymongo_mod

    gridfs_mod = types.ModuleType("gridfs")
    class GridFSStub:
        def __init__(self, db):
            pass

        def find_one(self, query):
            return None

    gridfs_mod.GridFS = GridFSStub
    sys.modules["gridfs"] = gridfs_mod

    # Mock LlamaCPP so it does not try to load a real model
    class DummyLlama:
        def __init__(self, *args, **kwargs):
            pass

    # Import job_matcher and replace LlamaCPP in its namespace with DummyLlama.
    import backend.app.job_matcher as jm

    jm.LlamaCPP = DummyLlama

    # Prevent MongoDB access by mocking get_user_raw_file
    monkeypatch.setattr(jm, 'get_user_raw_file', lambda email: b"")

    # Build a tiny fake index object that has as_query_engine returning an object with query()
    class FakeQueryEngine:
        def query(self, text):
            class Resp:
                source_nodes = []

            return Resp()

    class FakeIndex:
        def as_query_engine(self, similarity_top_k=5):
            return FakeQueryEngine()

    # Monkeypatch load_index_from_storage to return our fake index
    monkeypatch.setattr(jm, 'load_index_from_storage', lambda storage_context: FakeIndex())

    # Call match_jobs and assert it returns structure without raising
    result = jm.match_jobs(email, jobs=[])  # empty jobs list
    assert isinstance(result, dict)
    assert 'matches' in result and 'raw_file' in result
