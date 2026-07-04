"""
agents/ocr_agent.py

OCR Agent

Extracts text from image and converts it into neat structured information.
"""

from tools.ocr import extract_text
from models.llm import invoke_llm


def ocr_agent(state):

    print("\n========== OCR Agent ==========\n")

    try:
        image_path = state.get("file_path")
        query = state.get("query", "")

        if not image_path:
            return {
                **state,
                "tool_output": "",
                "success": False,
                "error": "No image uploaded."
            }

        print(f"Reading Image : {image_path}")

        raw_text = extract_text(image_path)

        print("\nOCR Completed.\n")

        if raw_text.startswith("OCR Error"):
            return {
                **state,
                "tool_output": "",
                "success": False,
                "error": raw_text
            }

        prompt = f"""
You are an OCR Information Structuring Agent.

The user asked:
{query}

Raw OCR text:
-------------------------
{raw_text}
-------------------------

Your task:
Convert the noisy OCR text into clean, organized information.

Rules:
- Do NOT invent information.
- Use only the OCR text.
- Remove OCR noise, random symbols, borders, and repeated broken words.
- If this is a marks memo / academic memo, extract:
  Institute
  Document Type
  Student Name
  Hall Ticket Number
  Branch
  Exam Month/Year
  Subjects
  Result Summary
  SGPA
  Date of Issue
- If some field is unclear, write "Not clearly detected".
- Format neatly using headings and bullet points.
- Do not return raw messy OCR text unless user specifically asks for raw text.

Return clean structured information.
"""

        structured_output = invoke_llm(prompt)

        return {
            **state,
            "tool_output": structured_output,
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
        "query": "extract key information from this image",
        "intent": "OCR",
        "tool": "ocr",
        "file_path": "uploads/images/sample.png",
        "history": []
    }

    result = ocr_agent(state)

    print(result["tool_output"])