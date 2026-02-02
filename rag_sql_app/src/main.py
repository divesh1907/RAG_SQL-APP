from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from collections import defaultdict, deque

from .embedder import create_embeddings
from .retriever import retrieve_schema
from .sql_generator import generate_sql
from .db import PostgresAdapter

app = FastAPI(title="RAG SQL API")

SESSION_WINDOW = 5
sessions = defaultdict(lambda: deque(maxlen=SESSION_WINDOW))
db = PostgresAdapter()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, example="")


@app.get("/health")
def health():
    return {"api": "ok"}


@app.post("/query")
def query(req: QueryRequest):
    try:
        history = list(sessions["default"])
        sessions["default"].append(req.question)

        collection = create_embeddings()
        tables, columns = retrieve_schema(
            collection,
            history + [req.question]
        )

        sql = generate_sql(req.question, history, tables, columns)
        result = db.execute(sql)

        return {
            "sql": sql,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))