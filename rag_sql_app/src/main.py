import re
from collections import deque
from embedder import create_embeddings
from retriever import retrieve_schema
from sql_generator import generate_sql
from db import run_sql
from answer_generator import generate_answer


# ---------- CONFIG ----------
CONTEXT_WINDOW_SIZE = 5   # number of past user queries to remember


# ---------- INTENT DETECTION ----------
def detect_intent(query: str) -> str:
    q = query.lower()
    if "vaccin" in q:
        return "vaccination_analysis"
    if "medication" in q or "medicine" in q:
        return "medication_analysis"
    if "patient" in q:
        return "patient_analysis"
    if "hospital" in q:
        return "hospital_analysis"
    return "generic"


# ---------- SLOT EXTRACTION ----------
def extract_slots(query: str) -> dict:
    slots = {}

    hospital_match = re.search(r"in\s+([a-zA-Z ]+ hospital)", query.lower())
    if hospital_match:
        slots["hospital"] = hospital_match.group(1).title()

    city_match = re.search(r"in\s+([a-zA-Z ]+)", query.lower())
    if city_match:
        slots["city"] = city_match.group(1).title()

    return slots


# ---------- FOLLOW-UP DETECTION ----------
def is_follow_up(query: str) -> bool:
    return query.lower().startswith(("what about", "and", "how about"))


# ---------- MAIN ----------
def main():
    print("\n🩺 Healthcare Conversational RAG-SQL Assistant")
    print("Ask questions freely.")
    print("Type 'exit' or 'quit' to stop.\n")

    # Create embeddings once
    collection = create_embeddings()

    # Session-level context
    context = {
        "history": deque(maxlen=CONTEXT_WINDOW_SIZE),
        "intent": None,
        "slots": {}
    }

    while True:
        user_query = input("Ask: ").strip()

        if user_query.lower() in {"exit", "quit"}:
            print("👋 Exiting. Goodbye!")
            break

        if not user_query:
            print("❌ Empty query. Try again.\n")
            continue

        # Add raw user query to history
        context["history"].append(user_query)

        # Detect intent (carry forward if follow-up)
        if not is_follow_up(user_query):
            context["intent"] = detect_intent(user_query)

        # Extract slots and MERGE with existing context
        new_slots = extract_slots(user_query)
        context["slots"].update({k: v for k, v in new_slots.items() if v})

        # Retrieve relevant schema using Chroma
        tables, columns = retrieve_schema(collection, user_query)

        print("📌 Tables from Chroma:", tables)
        print("📌 Columns from Chroma:", columns)
        print("🧠 Current Context:", context)

        # Generate SQL USING FULL CONTEXT WINDOW
        sql = generate_sql(
            user_query=user_query,
            context=context,
            tables=tables,
            columns=columns
        )

        print("\n🧠 Generated SQL:\n", sql)

        # Execute SQL (read-only)
        result = run_sql(sql)

        # Generate final answer
        answer = generate_answer(result, user_query)
        print("\n✅ Answer:\n", answer, "\n")


if __name__ == "__main__":
    main()