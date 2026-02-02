from .config import client
from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def generate_sql(question, context, tables, columns):
    prompt = f"""
You are a PostgreSQL expert.

Conversation history:
{context}

Allowed tables:
{tables}

Allowed columns:
{columns}

Schema:
- hospitals(hospital_id, hospital_name, city, state)
- patients(patient_id, patient_name, age, gender, hospital_id)
- vaccinations(patient_id, vaccine_name, vaccination_date, dose_number)
- medications(patient_id, medicine_name, dosage, start_date, end_date)

Rules:
- PostgreSQL only
- SELECT only
- Infer follow-up meaning from context
- Output ONLY SQL

User question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        timeout=15
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty LLM response")

    return content.replace("```sql", "").replace("```", "").strip()