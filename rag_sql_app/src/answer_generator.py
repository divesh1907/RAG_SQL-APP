from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed
from .config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def generate_answer(question: str, rows: list) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        timeout=15,
        messages=[
            {
                "role": "system",
                "content": "Answer clearly using the SQL result."
            },
            {
                "role": "user",
                "content": f"Question: {question}\nResult: {rows}"
            }
        ]
    )

    if not response.choices:
        return "No answer generated."

    return response.choices[0].message.content.strip()