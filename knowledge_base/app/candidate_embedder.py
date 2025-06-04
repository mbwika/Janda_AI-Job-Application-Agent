
# candidate_embedder.py

from llama_index.core.schema import Document
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core import ServiceContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import os

def embed_candidate(text):
    document = Document(text=text)
    embed_model = HuggingFaceEmbedding(model_name="hkunlp/instructor-xl")
    # Settings.embed_model = HuggingFaceEmbedding(model_name="hkunlp/instructor-xl")
    node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    Settings.embed_model = embed_model
    Settings.node_parser = node_parser


    # Create FAISS store directory
    import faiss
    faiss_save_path = "faiss_index/index.faiss"
    if os.path.exists(faiss_save_path):
        faiss_index = faiss.read_index(faiss_save_path)
    else:
        faiss_index = faiss.IndexFlatL2(768)  # 768 is the embedding dimension for instructor-xl
    faiss_store = FaissVectorStore(faiss_index=faiss_index)

    # Build index using Faiss store
    index = VectorStoreIndex.from_documents([document], service_context=Settings.embed_model, vector_store=faiss_store)
    documents = SimpleDirectoryReader("docs").load_data()
    from llama_index.core import StorageContext, load_index_from_storage
    index = VectorStoreIndex.from_documents(documents)

    storage_context = StorageContext.from_defaults(persist_dir="faiss_index")
    index = load_index_from_storage(storage_context)

    # Persist full index (FAISS + metadata)
    index.storage_context.persist(persist_dir="faiss_index")

    # Save the FAISS index
    faiss.write_index(faiss_index, faiss_save_path)

    return index
