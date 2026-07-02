"""
tools/image_caption.py

Image Captioning Tool

Uses BLIP model from Hugging Face to generate
a natural language caption for an uploaded image.
"""

from PIL import Image

from transformers import BlipProcessor, BlipForConditionalGeneration


# --------------------------------------------------
# Load BLIP Model
# --------------------------------------------------

print("Loading Image Captioning Model...")

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

print("Image Captioning Model Loaded.")


# --------------------------------------------------
# Caption Function
# --------------------------------------------------

def generate_caption(image_path: str) -> str:
    """
    Generate a caption for the given image.

    Args:
        image_path: Path of uploaded image

    Returns:
        Caption text
    """

    try:

        image = Image.open(image_path).convert("RGB")

        inputs = processor(
            image,
            return_tensors="pt"
        )

        output = model.generate(
            **inputs,
            max_new_tokens=50
        )

        caption = processor.decode(
            output[0],
            skip_special_tokens=True
        )

        return caption

    except Exception as e:

        return f"Image Captioning Error: {str(e)}"


# --------------------------------------------------
# Manual Test
# --------------------------------------------------

if __name__ == "__main__":

    image_path = "uploads/images/sample1.jpg"

    caption = generate_caption(image_path)

    print("\nGenerated Caption:\n")
    print(caption)