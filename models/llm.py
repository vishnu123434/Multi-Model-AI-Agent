"""
models/llm.py

Initializes the Large Language Model (LLM)
used across all agents in the application.
"""

import os
import re
from dotenv import load_dotenv

try:
    from langchain_groq import ChatGroq  # type: ignore[import]
except ImportError as exc:
    raise ImportError(
        "The langchain_groq package is required to initialize the Groq LLM. "
        "Install it with 'pip install langchain-groq'."
    ) from exc

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in .env file."
    )

# --------------------------------------------------
# Initialize LLM
# --------------------------------------------------

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=512,
)

# --------------------------------------------------
# Helper Function
# --------------------------------------------------
import re

def invoke_llm(prompt: str) -> str:
    response = llm.invoke(prompt)

    text = response.content if hasattr(response, "content") else str(response)

    # Case 1: complete think block
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    ).strip()

    # Case 2: incomplete think block
    if "<think>" in text:
        after_think = text.split("<think>", 1)[1]

        # Try to recover final answer from common markers
        markers = [
            "Final answer:",
            "Answer:",
            "\n\n-",
            "\n\nThe",
            "\n\nHyderabad",
            "\n\nIndia",
            "\n\nTelangana",
        ]

        recovered = ""

        for marker in markers:
            if marker in after_think:
                recovered = after_think.split(marker, 1)[1].strip()

                if marker.startswith("\n\n-"):
                    recovered = "- " + recovered
                elif marker.startswith("\n\n"):
                    recovered = marker.strip() + " " + recovered

                break

        if recovered:
            text = recovered
        else:
            # Last fallback: remove the <think> tag itself but keep text
            text = after_think.replace("<think>", "").strip()

    # Remove remaining tags if any
    text = text.replace("</think>", "").strip()

    if not text:
        text = "No clean answer was generated. Please try again."

    return text