import json
import re

from models.llm import invoke_llm
from tools.currency import extract_currency_details


def is_currency_query(query: str) -> bool:
    query = query.lower()

    currency_words = [
        "currency", "convert", "exchange", "money",
        "dollar", "dollars", "rupee", "rupees", "euro", "euros",
        "pound", "pounds", "yen", "dirham", "dirhams", "riyal",
        "riyals", "dinar", "dinars", "baht", "franc", "peso",
        "lira", "won", "yuan",
        "usd", "inr", "eur", "gbp", "jpy", "aed", "sar", "kwd",
        "qar", "omr", "bhd", "aud", "cad", "sgd", "chf", "cny",
        "krw", "thb", "myr", "npr", "pkr", "bdt", "lkr"
    ]

    return any(word in query for word in currency_words)



def is_image_ocr_query(query: str) -> bool:
    query = query.lower()

    return any(word in query for word in [
        "extract text",
        "extract info",
        "extract information",
        "read image",
        "read this image",
        "read screenshot",
        "read receipt",
        "ocr"
    ])


def is_image_caption_query(query: str) -> bool:
    query = query.lower()

    return any(word in query for word in [
        "describe image",
        "describe this image",
        "caption image",
        "caption this image",
        "what is in this image"
    ])


def planner(state):

    print("\n========== Planner Agent ==========\n")

    user_query = state["query"]
    forced_tool = state.get("forced_tool")

    # ------------------------------------
    # Uploaded file route: trust app.py
    # ------------------------------------

    if forced_tool:

       
        if forced_tool == "ocr":
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

    # ------------------------------------
    # Deterministic routes first
    # ------------------------------------

    if is_currency_query(user_query):

        currency_details = extract_currency_details(user_query)

        return {
            "query": user_query,
            "intent": "Currency Conversion",
            "tool": "currency",
            "amount": currency_details["amount"],
            "from_currency": currency_details["from_currency"],
            "to_currency": currency_details["to_currency"],
            "file_path": state.get("file_path"),
            "db_path": state.get("db_path"),
            "forced_tool": state.get("forced_tool"),
            "tool_output": None,
            "response": None,
            "success": True,
            "error": None,
            "history": state.get("history", [])
        }

    

    if is_image_ocr_query(user_query) and state.get("file_path"):

        return {
            "query": user_query,
            "intent": "OCR",
            "tool": "ocr",
            "amount": None,
            "from_currency": None,
            "to_currency": None,
            "file_path": state.get("file_path"),
            "db_path": state.get("db_path"),
            "forced_tool": state.get("forced_tool"),
            "tool_output": None,
            "response": None,
            "success": True,
            "error": None,
            "history": state.get("history", [])
        }

    if is_image_caption_query(user_query) and state.get("file_path"):

        return {
            "query": user_query,
            "intent": "Image Captioning",
            "tool": "image",
            "amount": None,
            "from_currency": None,
            "to_currency": None,
            "file_path": state.get("file_path"),
            "db_path": state.get("db_path"),
            "forced_tool": state.get("forced_tool"),
            "tool_output": None,
            "response": None,
            "success": True,
            "error": None,
            "history": state.get("history", [])
        }

    # ------------------------------------
    # Default: Web Search
    # ------------------------------------

    prompt = f"""
You are a planner for a Multi-Model AI Assistant.

Classify the current user question.

Important:
- Do NOT use previous conversation unless the current question clearly uses words like it, this, that, he, she, they, more, continue.
- Fresh factual questions must use Web Search.
- Questions about people, politics, current affairs, places, capitals, population, weather, CM, PM, CEO must use Web Search.
- Only use Document QA when the user clearly refers to an uploaded document/pdf/file.

Return ONLY valid JSON.

Available tools:
1. web
2. document
3. ocr
4. image
5. currency

Current user question:
{user_query}

Return format:
{{
"intent":"",
"tool":"web",
"resolved_query":""
}}
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

    # Safety override: avoid accidental document routing without db_path
    if plan.get("tool") == "document" and not state.get("db_path"):
        plan["tool"] = "web"
        plan["intent"] = "Web Search"

    resolved_query = plan.get("resolved_query", user_query)

    print("\nPlanner Result")
    print(plan)

    return {
        "query": resolved_query,
        "intent": plan.get("intent", "Web Search"),
        "tool": plan.get("tool", "web"),
        "amount": None,
        "from_currency": None,
        "to_currency": None,
        "file_path": state.get("file_path"),
        "db_path": state.get("db_path"),
        "forced_tool": state.get("forced_tool"),
        "tool_output": None,
        "response": None,
        "success": True,
        "error": None,
        "history": state.get("history", [])
    }