import json
import os
import chromadb
from chromadb.config import Settings


def create_embeddings():
    """
    Creates or loads ChromaDB embeddings for the database schema.
    Paths are resolved safely regardless of where Python is run from.
    """

    # Resolve project root: rag_sql_app/
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    DATA_PATH = os.path.join(BASE_DIR, "data", "health_code.json")
    CHROMA_PATH = os.path.join(BASE_DIR, "embeddings", "chroma_store")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Schema file not found at: {DATA_PATH}")

    client = chromadb.Client(
        Settings(persist_directory=CHROMA_PATH)
    )

    collection = client.get_or_create_collection("schema_embeddings")

    # If embeddings already exist, reuse them
    if collection.count() > 0:
        return collection

    with open(DATA_PATH, "r") as f:
        schema = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for table in schema["tables"]:
        table_name = table["table_name"]

        for column in table["columns"]:
            text = f"{table_name} {column['name']} {column.get('description', '')}"
            documents.append(text)
            metadatas.append({
                "table": table_name,
                "column": column["name"]
            })
            ids.append(f"{table_name}_{column['name']}")

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    return collection