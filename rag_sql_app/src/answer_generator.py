from .config import client


def generate_answer(question, sql, result):
    prompt = f"""
Question: {question}
SQL: {sql}
Result: {result}

Explain the result clearly.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()