import json
import re

from models.llm import invoke_llm
from tools.currency import extract_currency_details


def format_history(history):
    """
    Convert recent chat history into readable text for planner.
    """

    if not history:
        return "No previous conversation."

    lines = []

    for item in history:
        user_msg = item.get("user", "")
        ai_msg = item.get("assistant", "")

        lines.append(f"User: {user_msg}")
        lines.append(f"AI: {ai_msg}")

    return "\n".join(lines)


def is_currency_query(query: str) -> bool:
    """
    Detect currency conversion queries without depending only on LLM.
    """

    query = query.lower()

    currency_words = [
        "currency",
        "convert",
        "exchange",
        "money",

        "dollar",
        "dollars",
        "rupee",
        "rupees",
        "euro",
        "euros",
        "pound",
        "pounds",
        "yen",
        "dirham",
        "dirhams",
        "riyal",
        "riyals",
        "dinar",
        "dinars",
        "baht",
        "franc",
        "peso",
        "lira",
        "won",
        "yuan",

        "usd",
        "inr",
        "eur",
        "gbp",
        "jpy",
        "aed",
        "sar",
        "kwd",
        "qar",
        "omr",
        "bhd",
        "aud",
        "cad",
        "sgd",
        "chf",
        "cny",
        "krw",
        "thb",
        "myr",
        "npr",
        "pkr",
        "bdt",
        "lkr"
    ]

    return any(word in query for word in currency_words)


def planner(state):

    print("\n========== Planner Agent ==========\n")

    user_query = state["query"]
    forced_tool = state.get("forced_tool")

    if forced_tool:

     if forced_tool == "document":
        intent = "Document QA"
     elif forced_tool == "ocr":
        intent = "OCR"
     elif forced_tool == "image":
        intent = "Image Captioning"
     else:
        intent = "Web Search"

     return {
        "query": user_query,
        "intent": intent,
        "tool": forced_tool,
        "amount": None,
        "from_currency": None,
        "to_currency": None,
        "file_path": state.get("file_path"),
        "db_path": state.get("db_path"),
        "forced_tool": forced_tool,
        "tool_output": None,
        "response": None,
        "success": True,
        "error": None,
        "history": state.get("history", [])
    }
    history_text = format_history(state.get("history", []))

    # ------------------------------------
    # Direct currency detection first
    # ------------------------------------

    if is_currency_query(user_query):

        currency_details = extract_currency_details(user_query)

        plan = {
            "intent": "Currency Conversion",
            "tool": "currency",
            "resolved_query": user_query,
            "amount": currency_details["amount"],
            "from_currency": currency_details["from_currency"],
            "to_currency": currency_details["to_currency"]
        }

        print("\nPlanner Result")
        print(plan)

        return {
            "query": plan["resolved_query"],
            "intent": plan["intent"],
            "tool": plan["tool"],
            "amount": plan.get("amount"),
            "from_currency": plan.get("from_currency"),
            "to_currency": plan.get("to_currency"),
            "db_path": state.get("db_path"),
            "forced_tool": state.get("forced_tool"),
            "file_path": state.get("file_path"),
            "tool_output": None,
            "response": None,
            "success": True,
            "error": None,
            "history": state.get("history", [])
        }

    # ------------------------------------
    # LLM classification for non-currency
    # ------------------------------------

    prompt = f"""
You are the Planning Agent of a Multi-Model AI Assistant.

Your responsibilities:

1. Classify the user's request.
2. If the user asks a follow-up question, rewrite it into a clear standalone query using recent conversation.
3. Do NOT answer the question.
4. Return ONLY valid JSON.

-----------------------------------

Recent conversation:

{history_text}

-----------------------------------

Current user question:

{user_query}

-----------------------------------

Available tools:

1. Web Search
2. Currency Conversion
3. Document Question Answering / Summarization
4. OCR
5. Image Captioning

-----------------------------------

Classification Rules:

If the user asks about:
- latest news
- current information
- weather
- temperature
- humidity
- current people
- current posts
- search internet
- search web
- general factual questions

Return:

{{
"intent":"Web Search",
"tool":"web",
"resolved_query":"standalone rewritten query here"
}}

Example:

Recent conversation:
User: temp in gujarat
AI: The current temperature in Ahmedabad, Gujarat, is around 101°F.

Current user question:
tell me in celsius

Return:

{{
"intent":"Web Search",
"tool":"web",
"resolved_query":"current temperature in Ahmedabad Gujarat in Celsius"
}}

-----------------------------------

If user asks to convert currency:

Return:

{{
"intent":"Currency Conversion",
"tool":"currency",
"resolved_query":"standalone rewritten query here"
}}

-----------------------------------

If user uploads or refers to a PDF, DOCX, TXT, or document:

Examples:
Summarize this PDF
Summarize this document
Explain this document
Ask questions from document
Read this docx
Summarize this text file

Return:

{{
"intent":"Document QA",
"tool":"document",
"resolved_query":"standalone rewritten query here"
}}

-----------------------------------

If user wants text or information from image:

Examples:
Extract text
Extract info from image
Extract information from image
Read this bill
Read receipt
Read screenshot
Read this image
OCR

Return:

{{
"intent":"OCR",
"tool":"ocr",
"resolved_query":"standalone rewritten query here"
}}

-----------------------------------

If user asks to visually describe an image:

Examples:
Describe image
What is in this image
Caption image
Explain what is shown in image

Return:

{{
"intent":"Image Captioning",
"tool":"image",
"resolved_query":"standalone rewritten query here"
}}

-----------------------------------

If none match:

Return:

{{
"intent":"Web Search",
"tool":"web",
"resolved_query":"standalone rewritten query here"
}}

Return ONLY JSON.
"""

    response = invoke_llm(prompt)

    print("\nPlanner Raw Output:\n")
    print(response)

    match = re.search(r"\{.*\}", response, re.DOTALL)

    if not match:

        plan = {
            "intent": "Web Search",
            "tool": "web",
            "resolved_query": user_query
        }

    else:

        try:
            plan = json.loads(match.group())

        except Exception:

            plan = {
                "intent": "Web Search",
                "tool": "web",
                "resolved_query": user_query
            }

    # ------------------------------------
    # Safety: if LLM classified currency,
    # extract details using universal parser
    # ------------------------------------

    if plan.get("tool") == "currency":

        currency_details = extract_currency_details(user_query)

        plan["amount"] = currency_details["amount"]
        plan["from_currency"] = currency_details["from_currency"]
        plan["to_currency"] = currency_details["to_currency"]

    resolved_query = plan.get("resolved_query", user_query)

    print("\nPlanner Result")
    print(plan)

    return {
    "query": resolved_query,
    "intent": plan.get("intent", "Web Search"),
    "tool": plan.get("tool", "web"),
    "amount": plan.get("amount"),
    "from_currency": plan.get("from_currency"),
    "to_currency": plan.get("to_currency"),
    "file_path": state.get("file_path"),
    "db_path": state.get("db_path"),
    "forced_tool": state.get("forced_tool"),
    "tool_output": None,
    "response": None,
    "success": True,
    "error": None,
    "history": state.get("history", [])
}