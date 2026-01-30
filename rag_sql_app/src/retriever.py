def retrieve_schema(collection, query, k=4):
    """
    Returns a set of relevant tables and columns
    based on semantic similarity.
    """
    result = collection.query(
        query_texts=[query],
        n_results=k
    )

    tables = set()
    columns = set()

    for meta in result["metadatas"][0]:
        tables.add(meta["table"])
        columns.add(meta["column"])

    return list(tables), list(columns)
