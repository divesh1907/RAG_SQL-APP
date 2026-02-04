import threading
import chromadb
from chromadb.utils import embedding_functions
from .config import settings

_lock = threading.Lock()
_collection = None


def get_collection():
    global _collection
    if _collection is not None:
        return _collection

    with _lock:
        if _collection is None:
            client = chromadb.Client(
                chromadb.config.Settings(
                    persist_directory=settings.CHROMA_PATH
                )
            )

            # ✅ LOCAL embedding function (NO OpenAI)
            embedding_function = embedding_functions.DefaultEmbeddingFunction()

            _collection = client.get_or_create_collection(
                name="schema_embeddings",
                embedding_function=embedding_function
            )

    return _collection