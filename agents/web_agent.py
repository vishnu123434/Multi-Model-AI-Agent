"""
agents/web_agent.py

Web Search Agent

Calls the web search tool and stores
the retrieved information in the workflow state.
"""

from tools.web_search import web_search


def web_agent(state):

    print("\n========== Web Search Agent ==========\n")

    query = state["query"]

    print(f"Searching for: {query}")

    results = web_search(query)

    print("\nSearch Completed.\n")

    return {

        "query": state["query"],

        "intent": state["intent"],

        "tool": state["tool"],

        "file_path": state.get("file_path"),

        "tool_output": results,

        "response": None,

        "success": True,

        "error": None,

        "history": state.get("history", [])

    }