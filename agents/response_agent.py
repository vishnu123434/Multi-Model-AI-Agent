"""
agents/response_agent.py

Response Agent

Converts raw tool outputs into clean, concise,
user-friendly answers while keeping prompt size small.
"""

from models.llm import invoke_llm


MAX_TOOL_OUTPUT_CHARS = 3500


def limit_text(text: str, max_chars: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    if not text:
        return ""

    text = str(text)

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n\n[Content trimmed because it was too long.]"


def wants_detailed_answer(query: str) -> bool:
    detail_keywords = [
        "explain",
        "detail",
        "details",
        "summarize",
        "summary",
        "list",
        "points",
        "compare",
        "difference",
        "timeline",
        "why",
        "how",
        "steps",
        "full"
    ]

    query = query.lower()

    return any(word in query for word in detail_keywords)


def response_agent(state):

    print("\n========== Response Agent ==========\n")

    if not state.get("success"):

        return {
            **state,
            "response": state.get("error", "Something went wrong.")
        }

    query = state["query"]
    tool = state.get("tool")
    tool_output = state.get("tool_output", "")

    # ------------------------------------
    # Direct responses without LLM
    # ------------------------------------

    if tool == "currency":

        return {
            **state,
            "response": tool_output,
            "success": True,
            "error": None
        }

    if tool == "ocr":

        return {
            **state,
            "response": f"Extracted text:\n\n{tool_output}",
            "success": True,
            "error": None
        }

    if tool == "image":

        return {
            **state,
            "response": f"The image shows {tool_output}.",
            "success": True,
            "error": None
        }

    # ------------------------------------
    # Limit retrieved content before LLM
    # ------------------------------------

    limited_tool_output = limit_text(tool_output)

    detailed = wants_detailed_answer(query)

    if detailed:
        style_instruction = """
The user wants a detailed answer.
Use clear headings and bullet points.
Keep it useful and concise.
"""
    else:
        style_instruction = """
The user wants a direct answer.
Answer in 1 to 3 short sentences only.
Do NOT give background story, timeline, or extra details unless asked.
"""

    prompt = f"""
You are the Response Agent of a Multi-Model AI Assistant.

User question:
{query}

Retrieved information:
----------------------------------------
{limited_tool_output}
----------------------------------------

Rules:
1. Answer ONLY using the retrieved information.
2. Do NOT hallucinate.
3. Do NOT add unnecessary background.
4. If the user asks for a direct fact, answer directly.
5. If retrieved information is not useful, say no relevant information was found.
6. Keep the answer clean and professional.

{style_instruction}

Final answer:
"""

    try:

        answer = invoke_llm(prompt)

    except Exception as e:

        error_text = str(e)

        if "tokens per minute" in error_text or "Request too large" in error_text or "rate_limit" in error_text:
            answer = (
                "The retrieved content was too large for the current model limit. "
                "Please ask a shorter question or upload a smaller document section."
            )
        else:
            answer = f"Error while generating response: {error_text}"

    print("Final Response Generated.\n")

    return {
        **state,
        "response": answer,
        "success": True,
        "error": None
    }