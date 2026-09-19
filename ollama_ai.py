import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

MODEL = "llama3.2:3b"


def generate_minutes(transcript):

    prompt = f"""
You are an AI Meeting Assistant.

Create concise professional Minutes of Meeting from the transcript below.

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

        OLLAMA_URL,

        json={

            "model": MODEL,

            "prompt": prompt,

            "stream": False,

            "keep_alive": "5m",

            "options": {

                "temperature": 0.2,

                "num_predict": 500

            }

        },

        timeout=180

    )


    response.raise_for_status()


    data = response.json()


    return data.get(
        "response",
        "Unable to generate meeting minutes."
    )
