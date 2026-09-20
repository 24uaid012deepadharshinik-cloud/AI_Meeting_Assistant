import os
import requests


HF_URL = "https://router.huggingface.co/v1/chat/completions"

MODEL = "openai/gpt-oss-120b:fastest"


def generate_minutes(transcript):

    hf_token = os.getenv("HF_TOKEN")

    if not hf_token:
        raise RuntimeError(
            "HF_TOKEN is not configured."
        )

    prompt = f"""
Create professional Minutes of Meeting from the transcript below.

MEETING TRANSCRIPT:
{transcript}

Use exactly these sections:

1. Meeting Summary
2. Key Discussion Points
3. Decisions Made
4. Action Items
5. Assigned Persons
6. Deadlines

Rules:
- Use simple professional English.
- Be concise.
- Do not invent information.
- If information is missing, write "Not specified".
"""


    response = requests.post(

        HF_URL,

        headers={
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        },

        json={

            "model": MODEL,

            "messages": [

                {
                    "role": "system",
                    "content":
                        "You are a professional AI Meeting Assistant."
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            "temperature": 0.2,

            "max_tokens": 500,

            "stream": False

        },

        timeout=180
    )


    response.raise_for_status()

    data = response.json()


    return data["choices"][0]["message"]["content"].strip()
