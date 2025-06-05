

# candidate_embedder.py

from llama_index.core.schema import Document
from llama_index.core.indices.vector_store import VectorStoreIndex
# from llama_index.core import ServiceContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core import StorageContext
import os

def embed_candidate(email, text):
    from llama_index.core.schema import Document
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.vector_stores.faiss import FaissVectorStore
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core import Settings, StorageContext, VectorStoreIndex
    import os
    import faiss

    document = Document(text=text)
    embed_model = HuggingFaceEmbedding(model_name="hkunlp/instructor-xl")
    node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    Settings.embed_model = embed_model
    Settings.node_parser = node_parser

    # Create candidate directory if not exists
    user_index_dir = os.path.join("faiss_index", email)
    index_path = os.path.join(user_index_dir, "index.faiss")
    os.makedirs(user_index_dir, exist_ok=True)

    # Load or create FAISS index
    if os.path.exists(index_path):
        faiss_index = faiss.read_index(index_path)
    else:
        faiss_index = faiss.IndexFlatL2(768)  # 768 for instructor-xl

    # Build vector store
    faiss_store = FaissVectorStore(faiss_index=faiss_index)

    # Build and persist the index for this user
    index = VectorStoreIndex.from_documents([document], vector_store=faiss_store)
    index.storage_context.persist(persist_dir=user_index_dir)

    # Save the FAISS index file
    faiss.write_index(faiss_index, index_path)

    return index

