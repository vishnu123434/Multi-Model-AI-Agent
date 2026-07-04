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


def planner(state):

    print("\n========== Planner Agent ==========\n")

    user_query = state["query"]
    forced_tool = state.get("forced_tool")

    # Uploaded image route from app.py
    if forced_tool:

        if forced_tool == "ocr":
            intent = "OCR"

        elif forced_tool == "image":
            intent = "Image Captioning"

        elif forced_tool == "image_analysis":
            intent = "Image Analysis"

        else:
            intent = "Web Search"
            forced_tool = "web"

        result = {
            "query": user_query,
            "intent": intent,
            "tool": forced_tool,
            "amount": None,
            "from_currency": None,
            "to_currency": None,
            "file_path": state.get("file_path"),
            "forced_tool": forced_tool,
            "tool_output": None,
            "response": None,
            "success": True,
            "error": None,
            "history": state.get("history", [])
        }

        print("Planner Result")
        print(result)

        return result

    # Currency route
    if is_currency_query(user_query):

        currency_details = extract_currency_details(user_query)

        result = {
            "query": user_query,
            "intent": "Currency Conversion",
            "tool": "currency",
            "amount": currency_details["amount"],
            "from_currency": currency_details["from_currency"],
            "to_currency": currency_details["to_currency"],
            "file_path": state.get("file_path"),
            "forced_tool": None,
            "tool_output": None,
            "response": None,
            "success": True,
            "error": None,
            "history": state.get("history", [])
        }

        print("Planner Result")
        print(result)

        return result

    # Default route: Web Search
    result = {
        "query": user_query,
        "intent": "Web Search",
        "tool": "web",
        "amount": None,
        "from_currency": None,
        "to_currency": None,
        "file_path": state.get("file_path"),
        "forced_tool": None,
        "tool_output": None,
        "response": None,
        "success": True,
        "error": None,
        "history": state.get("history", [])
    }

    print("Planner Result")
    print(result)

    return result