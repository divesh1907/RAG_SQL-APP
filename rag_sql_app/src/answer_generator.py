from config import client

def generate_answer(sql_result, user_query):
    prompt = f"""
User question:
{user_query}

SQL result:
{sql_result}

Explain the answer clearly in natural language.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()