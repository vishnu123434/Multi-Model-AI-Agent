"""
tools/ocr.py

Stable OCR Tool using Tesseract.
Much lighter than EasyOCR for CPU/RAM demo.
"""

import os
import tempfile

from PIL import Image, ImageOps
import pytesseract


# Update this path if your install path is different
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

MAX_IMAGE_SIDE = 1400


def preprocess_image(image_path: str) -> str:
    image = Image.open(image_path).convert("RGB")

    width, height = image.size
    max_side = max(width, height)

    if max_side > MAX_IMAGE_SIDE:
        scale = MAX_IMAGE_SIDE / max_side
        image = image.resize(
            (int(width * scale), int(height * scale)),
            Image.LANCZOS
        )

    image = ImageOps.grayscale(image)

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png"
    )

    processed_path = temp_file.name
    temp_file.close()

    image.save(processed_path)

    return processed_path


def extract_text(image_path: str) -> str:
    processed_path = None

    try:
        if not os.path.exists(image_path):
            return f"OCR Error: Image not found: {image_path}"

        processed_path = preprocess_image(image_path)

        text = pytesseract.image_to_string(
            processed_path,
            lang="eng",
            config="--psm 6"
        )

        text = text.strip()

        if not text:
            return "No text detected."

        return text

    except Exception as e:
        return f"OCR Error: {str(e)}"

    finally:
        if processed_path and os.path.exists(processed_path):
            os.remove(processed_path)


if __name__ == "__main__":
    print(extract_text("uploads/images/sample.png"))