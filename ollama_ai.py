import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"


def generate_minutes(transcript):

    prompt = f"""
You are an AI Meeting Assistant.

Analyze the following meeting transcript and create professional
Minutes of Meeting.

MEETING TRANSCRIPT:
{transcript}

Give the output in these sections:

1. Meeting Summary
2. Key Discussion Points
3. Decisions Made
4. Action Items
5. Assigned Persons
6. Deadlines

Use simple and professional English.
Do not invent information.
If something is not mentioned, write "Not specified".
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"]