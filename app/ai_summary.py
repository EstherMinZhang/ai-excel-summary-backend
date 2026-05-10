import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_ai_summary(structured_summary: dict) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
You are a data analyst. Please review this structured dataset summary and return:
1. A plain English summary of the dataset.
2. Any data quality issues.
3. Suggested next analysis steps.

Dataset summary:
{json.dumps(structured_summary, indent=2)}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "plain_english_summary": response.text
    }