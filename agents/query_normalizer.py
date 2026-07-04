"""
agents/query_normalizer.py

Query Normalizer Agent

Normalizes user queries.
Uses chat history only for clear follow-up questions.
"""

from models.llm import invoke_llm


FOLLOWUP_WORDS = {
    "it",
    "this",
    "that",
    "these",
    "those",
    "he",
    "she",
    "they",
    "them",
    "his",
    "her",
    "their",
    "its",
    "same",
    "again",
    "more",
    "continue",
    "previous",
    "above",
}


def format_history(history):
    if not history:
        return "No previous conversation."

    lines = []

    for item in history[-4:]:
        lines.append(f"User: {item.get('user', '')}")
        lines.append(f"AI: {item.get('assistant', '')}")

    return "\n".join(lines)


def is_followup_query(query: str) -> bool:
    words = query.lower().replace("?", "").replace(".", "").split()
    return any(word in FOLLOWUP_WORDS for word in words)


def query_normalizer(state):

    print("\n========== Query Normalizer Agent ==========\n")

    # If uploaded image exists, don't rewrite using history
    if state.get("forced_tool") or state.get("file_path"):
        print("Uploaded file detected. Skipping normalization.")
        return state

    query = state["query"]

    if is_followup_query(query):
        history = format_history(state.get("history", []))
    else:
        history = "No previous conversation."

    prompt = f"""
You are a Query Normalizer.

Your ONLY job is to rewrite the user's query into a clean standalone query.

Rules:
- Fix spelling mistakes, abbreviations, and broken English.
- Use previous conversation ONLY if the current query is clearly a follow-up.
- If the current query is a fresh question, ignore previous conversation completely.
- Do NOT answer the question.
- Do NOT add facts.
- Do NOT guess the answer.
- Do NOT replace the question with an answer.
- Do NOT add information that is not already implied by the user query.
- Return ONLY the rewritten query.
- No JSON.
- No explanation.

Examples:

Input:
Capital of Kazakhstan

Output:
What is the capital of Kazakhstan?

Input:
cm of telangana

Output:
Who is the Chief Minister of Telangana?

Input:
wht is popultion of tg

Output:
What is the population of Telangana?

Input:
latest ai news today

Output:
Latest AI news today

Previous conversation:
User: temperature in Hyderabad
AI: Hyderabad temperature is 24°C.

Current user query:
tell me in fahrenheit

Output:
Current temperature in Hyderabad in Fahrenheit

Previous conversation:
{history}

Current user query:
{query}

Output:
"""

    normalized_query = invoke_llm(prompt).strip()

    # -------------------------------
    # Safety Guard:
    # Prevent normalizer from answering
    # -------------------------------

    fresh_question_keywords = [
        "capital",
        "who",
        "what",
        "where",
        "when",
        "why",
        "how",
        "cm",
        "pm",
        "ceo",
        "population",
        "temperature",
        "weather",
    ]

    bad_answer_patterns = [
        "official",
        "largest city",
        "is the",
        "is a",
        "was the",
        "are the",
    ]

    query_lower = query.lower()
    normalized_lower = normalized_query.lower()

    if any(word in query_lower for word in fresh_question_keywords):
        if any(pattern in normalized_lower for pattern in bad_answer_patterns):
            normalized_query = query

    # Extra cleanup
    normalized_query = normalized_query.replace("Output:", "").strip()

    if not normalized_query:
        normalized_query = query

    print("Original Query:", query)
    print("Normalized Query:", normalized_query)

    return {
        **state,
        "query": normalized_query
    }