"""
Extraction Service

Sends verified OCR text to Groq and parses structured medicine JSON.

NEVER invents missing fields - uses null when information isn't present.
"""

import json
import os
from typing import List, Optional

from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")


class MedicineInfo(BaseModel):
    name: Optional[str] = None
    strength: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    timing: Optional[str] = None
    food_relation: Optional[str] = None
    duration: Optional[str] = None


EXTRACTION_SYSTEM_PROMPT = """You are a strict information extraction engine
for prescription text.

Rules:

1. Extract ONLY information explicitly present in the given prescription text.

2. NEVER infer, guess, or invent dosage, timing, frequency, strength,
duration, food relation, or medical information.

3. If a field is not mentioned, set it to null.

4. Return ONLY valid JSON.
Do not return markdown.
Do not return explanations.
Do not return commentary.

5. Output format must be a JSON array of objects with this exact schema:

[
  {
    "name": "string or null",
    "strength": "string or null",
    "dosage": "string or null",
    "frequency": "string or null",
    "timing": "string or null",
    "food_relation": "string or null",
    "duration": "string or null"
  }
]

6. If no medicines can be identified, return:

[]
"""


def _call_llm(system_prompt: str, user_message: str) -> str:

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Please configure your .env file."
        )

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        max_tokens=1500,
        temperature=0
    )

    return response.choices[0].message.content.strip()


def _clean_json_response(raw_text: str) -> str:

    """Remove markdown code fences if the model returns them."""

    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        parts = cleaned.split("```")

        if len(parts) >= 3:
            cleaned = parts[1]

            if cleaned.startswith("json"):
                cleaned = cleaned[4:]

    return cleaned.strip()


def extract_medicines(prescription_text: str) -> List[MedicineInfo]:

    """
    Extract structured medicine information from prescription text.

    Missing fields are returned as null.
    """

    user_message = (
        f"Prescription text:\n\n"
        f"{prescription_text}\n\n"
        f"Extract the medicines as JSON."
    )

    raw_response = _call_llm(
        EXTRACTION_SYSTEM_PROMPT,
        user_message
    )

    cleaned = _clean_json_response(raw_response)

    try:
        parsed = json.loads(cleaned)

    except json.JSONDecodeError:
        raise RuntimeError(
            "Could not parse a valid medicine list from the LLM response. "
            "Please verify the prescription text and try again."
        )

    if not isinstance(parsed, list):
        raise RuntimeError(
            "Unexpected response format from LLM extraction."
        )

    medicines = []

    for item in parsed:

        if isinstance(item, dict):
            medicines.append(
                MedicineInfo(**item)
            )

    return medicines