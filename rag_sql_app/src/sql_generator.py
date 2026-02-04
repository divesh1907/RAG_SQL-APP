from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed
from .config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a senior PostgreSQL data engineer.

Schema:
- hospitals(hospital_id, hospital_name, city, state)
- patients(patient_id, patient_name, age, gender, hospital_id)
- vaccinations(patient_id, vaccine_name, vaccination_date, dose_number)
- medications(patient_id, medicine_name, dosage, start_date, end_date)

Rules:
- PostgreSQL syntax ONLY
- SELECT statements ONLY
- NO INSERT, UPDATE, DELETE, DROP, ALTER
- Infer follow-up meaning from conversation context
- Use proper JOINs and foreign keys
- Output ONLY raw SQL
- No explanations
- No markdown
"""

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def generate_sql(
    question: str,
    schema_context: list,
    conversation_history: list | None = None
) -> str:
    """
    Generates a safe PostgreSQL SELECT query.
    """

    retrieved_context = "\n".join(
        f"{x['table']}.{x['column']}" for x in schema_context
        if x.get("table") and x.get("column")
    )

    history_block = ""
    if conversation_history:
        history_block = "\n".join(conversation_history[-5:])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        timeout=15,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Conversation Context:
{history_block}

Relevant Schema Hints:
{retrieved_context}

User Question:
{question}
"""
            }
        ]
    )

    # Defensive normalization
    if not response.choices:
        raise RuntimeError("LLM returned no choices")

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("Empty SQL generated")

    return content.strip()