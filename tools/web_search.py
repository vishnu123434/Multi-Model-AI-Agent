"""
tools/web_search.py

Live Web Search Tool using Tavily API.
Keeps results short to avoid LLM token limit errors.
"""

import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in .env")

client = TavilyClient(api_key=TAVILY_API_KEY)

MAX_RESULT_CHARS = 700


def trim_text(text: str) -> str:
    if not text:
        return ""

    if len(text) <= MAX_RESULT_CHARS:
        return text

    return text[:MAX_RESULT_CHARS] + "..."


def web_search(query: str) -> str:
    try:
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=3
        )

        if "results" not in response:
            return "No search results found."

        output = []

        for i, result in enumerate(response["results"], start=1):
            title = result.get("title", "No Title")
            content = trim_text(result.get("content", ""))
            url = result.get("url", "")

            output.append(
                f"""
Result {i}

Title:
{title}

Content:
{content}

Source:
{url}
"""
            )

        return "\n".join(output)

    except Exception as e:
        return f"Web Search Error: {str(e)}"