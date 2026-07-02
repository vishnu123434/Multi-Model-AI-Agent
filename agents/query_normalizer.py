"""
agents/query_normalizer.py

Query Normalizer Agent
Normalizes only normal text queries.
For uploaded files, it skips normalization to avoid mixing old history.
"""

from models.llm import invoke_llm


def format_history(history):
    if not history:
        return "No previous conversation."

    lines = []

    for item in history[-6:]:
        lines.append(f"User: {item.get('user', '')}")
        lines.append(f"AI: {item.get('assistant', '')}")

    return "\n".join(lines)


def query_normalizer(state):

    print("\n========== Query Normalizer Agent ==========\n")

    # IMPORTANT:
    # If user uploaded PDF/image, do not rewrite query using history.
    if state.get("forced_tool") or state.get("file_path"):
        print("Uploaded file detected. Skipping normalization.")
        return state

    query = state["query"]
    history = format_history(state.get("history", []))

    prompt = f"""
You are a Query Normalizer.

Rewrite the user's query into a clean standalone query.

Fix spelling mistakes, abbreviations, broken English, and follow-up references.

Do NOT answer.
Return ONLY the rewritten query.
No JSON.
No explanation.

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