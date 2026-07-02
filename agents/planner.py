import json
import re

from models.llm import invoke_llm
from tools.currency import extract_currency_details


def is_currency_query(query: str) -> bool:
    """
    Detect currency conversion queries without depending only on LLM.
    """

    query = query.lower()

    currency_words = [
        "currency",
        "convert",
        "exchange",
        "rate",
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

    # ------------------------------------
    # Direct currency detection first
    # ------------------------------------

    if is_currency_query(user_query):

        currency_details = extract_currency_details(user_query)

        plan = {
            "intent": "Currency Conversion",
            "tool": "currency",
            "amount": currency_details["amount"],
            "from_currency": currency_details["from_currency"],
            "to_currency": currency_details["to_currency"]
        }

        print("\nPlanner Result")
        print(plan)

        return {
            "query": state["query"],
            "intent": plan["intent"],
            "tool": plan["tool"],
            "amount": plan.get("amount"),
            "from_currency": plan.get("from_currency"),
            "to_currency": plan.get("to_currency"),
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

Your ONLY responsibility is to classify the user's request.

Do NOT answer the question.

Return ONLY valid JSON.

-----------------------------------

Available tools

1. Web Search
2. Currency Conversion
3. Document Question Answering / Summarization
4. OCR
5. Image Captioning

-----------------------------------

Classification Rules

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

Return

{{
"intent":"Web Search",
"tool":"web"
}}

-----------------------------------

If the user asks to convert currency.

Examples

Convert 100 USD to INR
100 dollars to rupees
1000 euros in dollars
500 EUR to GBP
Convert 25 GBP to USD
1000 rupees in dollars

Return

{{
"intent":"Currency Conversion",
"tool":"currency"
}}

-----------------------------------

If user uploads or refers to a PDF, DOCX, TXT, or document.

Examples

Summarize this PDF
Summarize this document
Explain this document
Ask questions from document
Read this docx
Summarize this text file

Return

{{
"intent":"Document QA",
"tool":"pdf"
}}

-----------------------------------

If user wants text or information from image.

Examples

Extract text
Extract info from image
Extract information from image
Read this bill
Read receipt
Read screenshot
Read this image
OCR

Return

{{
"intent":"OCR",
"tool":"ocr"
}}

-----------------------------------

If user asks to visually describe an image.

Examples

Describe image
What is in this image
Caption image
Explain what is shown in image

Return

{{
"intent":"Image Captioning",
"tool":"image"
}}

-----------------------------------

If none match

Return

{{
"intent":"Web Search",
"tool":"web"
}}

Question:

{user_query}
"""

    response = invoke_llm(prompt)

    print("\nPlanner Raw Output:\n")
    print(response)

    match = re.search(r"\{.*\}", response, re.DOTALL)

    if not match:

        plan = {
            "intent": "Web Search",
            "tool": "web"
        }

    else:

        try:
            plan = json.loads(match.group())

        except Exception:

            plan = {
                "intent": "Web Search",
                "tool": "web"
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

    print("\nPlanner Result")
    print(plan)

    return {
        "query": state["query"],
        "intent": plan.get("intent", "Web Search"),
        "tool": plan.get("tool", "web"),
        "amount": plan.get("amount"),
        "from_currency": plan.get("from_currency"),
        "to_currency": plan.get("to_currency"),
        "file_path": state.get("file_path"),
        "tool_output": None,
        "response": None,
        "success": True,
        "error": None,
        "history": state.get("history", [])
    }