"""
Chat Service

Answers user questions grounded ONLY in the prescription text
and extracted medicine data.
"""

import json
import os
from typing import List, Optional

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")


CHAT_SYSTEM_PROMPT = """You are PrescriptionLens AI's assistant.
You help a user understand ONE specific uploaded prescription.
You are an organizer/explainer, not a doctor.

STRICT RULES:

1. Answer using ONLY the prescription text and structured medicine data provided below.

2. If the user asks something that cannot be determined from the given prescription,
respond EXACTLY with:
"I cannot determine that from the uploaded prescription."

3. You MAY provide brief, general educational information about what a mentioned
medicine is commonly used for, but clearly label it as general educational
information, not a diagnosis or medical advice.

4. NEVER invent dosage, timing, frequency, strength, or duration information.

5. NEVER suggest changing medication, starting a new medication, or a treatment plan.

6. If there is medical uncertainty, tell the user to consult their doctor or pharmacist.

7. Keep answers concise and clear.
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
        max_tokens=800,
        temperature=0
    )

    return response.choices[0].message.content.strip()


def answer_question(
    question: str,
    prescription_text: str,
    medicines: Optional[List[dict]] = None
) -> str:

    """Build a grounded prompt and return the LLM's answer."""

    medicines = medicines or []

    context = (
        f"PRESCRIPTION TEXT:\n{prescription_text}\n\n"
        f"STRUCTURED MEDICINE DATA (JSON):\n"
        f"{json.dumps(medicines, indent=2)}\n\n"
        f"USER QUESTION:\n{question}"
    )

    try:
        answer = _call_llm(CHAT_SYSTEM_PROMPT, context)

    except RuntimeError:
        raise

    except Exception as e:
        raise RuntimeError(
            f"Failed to get a response from the AI service: {str(e)}"
        )

    if not answer:
        return "I cannot determine that from the uploaded prescription."

    return answer