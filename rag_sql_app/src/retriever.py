def retrieve_schema(collection, queries, top_k=5):
    results = collection.query(
        query_texts=queries,
        n_results=top_k
    )

    tables = set()
    columns = set()

    for meta_list in results.get("metadatas", []):
        for meta in meta_list or []:
            tables.add(meta["table"])
            columns.add(f"{meta['table']}.{meta['column']}")

    return list(tables), list(columns)