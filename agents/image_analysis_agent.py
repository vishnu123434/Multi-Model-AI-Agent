"""
agents/image_analysis_agent.py

Image Analysis Agent

Combines:
1. Image captioning
2. OCR text extraction
3. Image metadata
4. LLM-based structured image analysis
"""

from PIL import Image

from tools.image_caption import generate_caption
from tools.ocr import extract_text
from models.llm import invoke_llm


def get_image_metadata(image_path):
    image = Image.open(image_path)

    width, height = image.size

    if width > height:
        orientation = "Landscape"
    elif height > width:
        orientation = "Portrait"
    else:
        orientation = "Square"

    return {
        "width": width,
        "height": height,
        "orientation": orientation,
        "format": image.format
    }


def image_analysis_agent(state):

    print("\n========== Image Analysis Agent ==========\n")

    image_path = state.get("file_path")

    if not image_path:

        return {
            **state,
            "tool_output": "",
            "success": False,
            "error": "No image uploaded."
        }

    try:

        print("Analyzing Image:", image_path)

        caption = generate_caption(image_path)

        ocr_text = extract_text(image_path)

        metadata = get_image_metadata(image_path)

        prompt = f"""
You are an Image Intelligence Agent.

Analyze the uploaded image using the available extracted information.

Image Caption:
{caption}

OCR Extracted Text:
{ocr_text}

Image Metadata:
Width: {metadata["width"]}
Height: {metadata["height"]}
Orientation: {metadata["orientation"]}
Format: {metadata["format"]}

Create a structured image analysis.

Return in this format:

IMAGE ANALYSIS

1. Scene Description
Explain what the image shows.

2. Image Type
Classify the image type. Examples:
presentation slide, receipt, screenshot, document image, natural scene, product image, ID card, certificate, form, poster, diagram.

3. Visible / Detected Elements
List important visual elements.

4. Extracted Text
If OCR text is useful, show it clearly.
If no useful text exists, say "No readable text detected."

5. Key Information
Extract important points from the image.

6. Suggested Tags
Give 5 to 8 searchable tags.

7. Possible Use Cases
Mention where this image analysis can be useful.

Keep the answer clean, practical, and professional.
Do not hallucinate.
"""

        analysis = invoke_llm(prompt)

        return {
            **state,
            "tool_output": analysis,
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