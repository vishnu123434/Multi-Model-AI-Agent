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

Rewrite the user's query into a clean standalone query.

Rules:
- Fix spelling mistakes, abbreviations, and broken English.
- Use previous conversation ONLY if the current query is clearly a follow-up.
- If the current query is a fresh question, ignore previous conversation completely.
- Do NOT change the meaning.
- Do NOT answer.
- Return ONLY the rewritten query.
- No JSON.
- No explanation.

Examples:

Previous conversation:
User: explain AIML
AI: AIML means Artificial Intelligence Markup Language.

Current user query:
what is artificial intelligence

Rewritten query:
What is Artificial Intelligence?

Previous conversation:
User: temperature in Hyderabad
AI: Hyderabad temperature is 24°C.

Current user query:
tell me in fahrenheit

Rewritten query:
Current temperature in Hyderabad in Fahrenheit

Previous conversation:
User: who is Narendra Modi
AI: Narendra Modi is the Prime Minister of India.

Current user query:
capital of china

Rewritten query:
Capital of China

Previous conversation:
{history}

Current user query:
{query}

Rewritten query:
"""

    normalized_query = invoke_llm(prompt).strip()

    print("Original Query:", query)
    print("Normalized Query:", normalized_query)

    return {
        **state,
        "query": normalized_query
    }