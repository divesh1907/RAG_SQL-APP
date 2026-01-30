from config import client

def generate_sql(user_query, context, tables, columns):
    prompt = f"""
You are a PostgreSQL expert.

Conversation context (previous user queries):
{list(context["history"])}

Current intent:
{context["intent"]}

Active filters inferred from conversation:
{context["slots"]}

Relevant tables (MUST use only these):
{tables}

Relevant columns:
{columns}

Database schema:
- hospitals(hospital_id, hospital_name, city, state)
- patients(patient_id, patient_name, age, gender, hospital_id)
- vaccinations(patient_id, vaccine_name, vaccination_date, dose_number)
- medications(patient_id, medicine_name, dosage, start_date, end_date)

Relationships:
- hospitals.hospital_id = patients.hospital_id
- patients.patient_id = vaccinations.patient_id
- patients.patient_id = medications.patient_id

Rules:
- PostgreSQL syntax only
- SELECT queries only (read-only)
- Use correct JOINs
- Respect conversation context
- Use COUNT(DISTINCT patients.patient_id) where appropriate
- If asked about vaccinations, include vaccine_name
- Return ONLY SQL (no explanation)

User question:
{user_query}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return (
        response.choices[0].message.content
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )