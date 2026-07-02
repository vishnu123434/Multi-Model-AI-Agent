"""
tools/ocr.py

OCR Tool

Extracts text from an uploaded image using EasyOCR.
Includes image resizing to prevent CPU memory errors.
"""

import os
import tempfile

from PIL import Image
import easyocr


# Load OCR model once
reader = easyocr.Reader(
    ["en"],
    gpu=False
)


MAX_IMAGE_SIDE = 1400


def preprocess_image(image_path: str) -> str:
    """
    Resize large images before OCR to avoid memory errors.

    Returns:
        Path to processed temporary image.
    """

    image = Image.open(image_path).convert("RGB")

    width, height = image.size

    max_side = max(width, height)

    if max_side > MAX_IMAGE_SIDE:
        scale = MAX_IMAGE_SIDE / max_side

        new_width = int(width * scale)
        new_height = int(height * scale)

        image = image.resize(
            (new_width, new_height),
            Image.LANCZOS
        )

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".jpg"
    )

    processed_path = temp_file.name
    temp_file.close()

    image.save(
        processed_path,
        format="JPEG",
        quality=90
    )

    return processed_path


def extract_text(image_path: str) -> str:
    """
    Extract text from an image.

    Args:
        image_path: Path to image

    Returns:
        Extracted text
    """

    processed_path = None

    try:

        if not os.path.exists(image_path):
            return f"Image not found: {image_path}"

        processed_path = preprocess_image(image_path)

        results = reader.readtext(
            processed_path,
            detail=0,
            paragraph=True,
            canvas_size=1600,
            mag_ratio=1.0,
            batch_size=1
        )

        if not results:
            return "No text detected."

        return "\n".join(results)

    except Exception as e:

        return f"OCR Error: {str(e)}"

    finally:

        if processed_path and os.path.exists(processed_path):
            os.remove(processed_path)


if __name__ == "__main__":

    image = "uploads/images/sample.png"

    print(extract_text(image))