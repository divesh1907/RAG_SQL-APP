import json
import os
import chromadb
from chromadb.config import Settings

_collection = None


def create_embeddings():
    global _collection
    if _collection is not None:
        return _collection

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(BASE_DIR, "data", "health_code.json")
    CHROMA_PATH = os.path.join(BASE_DIR, "embeddings", "chroma_store")

    client = chromadb.Client(
        Settings(
            persist_directory=CHROMA_PATH,
            anonymized_telemetry=False
        )
    )

    collection = client.get_or_create_collection("schema_embeddings")

    if collection.count() > 0:
        _collection = collection
        return collection

    with open(DATA_PATH, "r") as f:
        schema = json.load(f)

    documents, metadatas, ids = [], [], []

    for table in schema["tables"]:
        for column in table["columns"]:
            documents.append(
                f"{table['table_name']} {column['name']} {column.get('description', '')}"
            )
            metadatas.append({
                "table": table["table_name"],
                "column": column["name"]
            })
            ids.append(f"{table['table_name']}::{column['name']}")

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    _collection = collection
    return collection