from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from .retriever import retrieve_schema
from .sql_generator import generate_sql
from .answer_generator import generate_answer
from .db import PostgresAdapter, UnsafeSQLError

app = FastAPI(
    title="RAG SQL API",
    version="0.1.0"
)

db = PostgresAdapter()

# In-memory conversation store (simple + safe for now)
conversation_history: List[str] = []


# =========================
# Request / Response Models
# =========================

class QueryRequest(BaseModel):
    question: str = Field(
        default="",
        description="Natural language question"
    )


class QueryResponse(BaseModel):
    sql: str
    rows: list
    answer: str


# =========================
# API Endpoints
# =========================


@app.get("/health")
def health_check():
    try:
        db.execute("SELECT 1")
        return {
            "status": "ok",
            "api": "running",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "api": "running",
            "database": "disconnected",
            "detail": str(e)
        }
    
@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # Maintain context window of last 5 questions
        conversation_history.append(req.question)
        recent_history = conversation_history[-5:]

        schema_context = retrieve_schema(req.question)

        sql = generate_sql(
            question=req.question,
            schema_context=schema_context,
            conversation_history=recent_history
        )

        rows = db.execute(sql)
        answer = generate_answer(req.question, rows)

        return QueryResponse(
            sql=sql,
            rows=rows,
            answer=answer
        )

    except UnsafeSQLError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))