"""
agents/currency_agent.py

Currency Agent

Extracts currency conversion details from the
planner output, calls the currency tool,
and stores the result in the workflow state.
"""

from tools.currency import convert_currency


def currency_agent(state):

    print("\n========== Currency Agent ==========\n")

    try:

        # -----------------------------------
        # Read planner output
        # -----------------------------------

        amount = state.get("amount", 1)

        from_currency = state.get("from_currency")

        to_currency = state.get("to_currency")

        print(
            f"Converting {amount} "
            f"{from_currency} -> {to_currency}"
        )

        # -----------------------------------
        # Perform Conversion
        # -----------------------------------

        result = convert_currency(

            amount=amount,

            from_currency=from_currency,

            to_currency=to_currency

        )

        return {

            "query": state["query"],

            "intent": state["intent"],

            "tool": state["tool"],

            "file_path": state.get("file_path"),

            "tool_output": result["message"],

            "response": None,

            "success": result["success"],

            "error": None if result["success"] else result["message"],

            "history": state.get("history", [])

        }

    except Exception as e:

        return {

            "query": state["query"],

            "intent": state["intent"],

            "tool": state["tool"],

            "file_path": state.get("file_path"),

            "tool_output": "",

            "response": None,

            "success": False,

            "error": str(e),

            "history": state.get("history", [])

        }


# -----------------------------------
# Manual Test
# -----------------------------------

if __name__ == "__main__":

    state = {

        "query": "Convert 100 USD to INR",

        "intent": "Currency",

        "tool": "currency",

        "amount": 100,

        "from_currency": "USD",

        "to_currency": "INR",

        "history": []

    }

    result = currency_agent(state)

    print(result)