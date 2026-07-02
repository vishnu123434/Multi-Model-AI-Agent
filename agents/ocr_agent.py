"""
agents/ocr_agent.py

OCR Agent

Uses the OCR tool to extract text
from an uploaded image.
"""

from tools.ocr import extract_text


def ocr_agent(state):

    print("\n========== OCR Agent ==========\n")

    try:

        image_path = state.get("file_path")

        if not image_path:

            return {
                **state,
                "tool_output": "",
                "success": False,
                "error": "No image uploaded."
            }

        print(f"Reading Image : {image_path}")

        text = extract_text(image_path)

        print("\nOCR Completed.\n")

        if text.startswith("OCR Error"):

            return {
                **state,
                "tool_output": "",
                "success": False,
                "error": text
            }

        return {
            **state,
            "tool_output": text,
            "success": True,
            "error": None
        }

    except Exception as e:

        return {
            **state,
            "tool_output": "",
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":

    state = {
        "query": "Extract text",
        "intent": "OCR",
        "tool": "ocr",
        "file_path": "uploads/images/sample.png",
        "history": []
    }

    result = ocr_agent(state)

    print(result["tool_output"])