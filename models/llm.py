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
    model="qwen/qwen3-32b",
    temperature=0,
    max_tokens=1024,
)

# --------------------------------------------------
# Helper Function
# --------------------------------------------------

def invoke_llm(prompt):

    response = llm.invoke(prompt)

    text = response.content if hasattr(response, "content") else str(response)

    # Remove reasoning blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    return text.strip()