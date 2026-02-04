from typing import List, Dict
from .embedder import get_collection

def retrieve_schema(question: str, k: int = 6) -> List[Dict]:
    collection = get_collection()

    results = collection.query(
        query_texts=[question],
        n_results=k
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    scores = results.get("distances", [[]])[0]

    context = []
    for doc, meta, score in zip(docs, metas, scores):
        context.append({
            "text": doc,
            "table": meta.get("table"),
            "column": meta.get("column"),
            "score": score
        })

    return context