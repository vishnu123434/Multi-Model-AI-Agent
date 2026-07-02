"""
agents/image_agent.py

Image Captioning Agent

Uses the image captioning tool to describe
an uploaded image.
"""

from tools.image_caption import generate_caption


def image_agent(state):

    print("\n========== Image Captioning Agent ==========\n")

    try:

        image_path = state.get("file_path")

        if not image_path:

            return {
                **state,
                "tool_output": "",
                "response": None,
                "success": False,
                "error": "No image uploaded."
            }

        print(f"Describing Image : {image_path}")

        caption = generate_caption(image_path)

        print("\nImage Caption Generated.\n")

        return {
            **state,
            "tool_output": caption,
            "response": None,
            "success": True,
            "error": None
        }

    except Exception as e:

        return {
            **state,
            "tool_output": "",
            "response": None,
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":

    state = {
        "query": "Describe this image",
        "intent": "Image Captioning",
        "tool": "image",
        "amount": None,
        "from_currency": None,
        "to_currency": None,
        "file_path": "uploads/images/sample1.jpg",
        "tool_output": None,
        "response": None,
        "success": True,
        "error": None,
        "history": []
    }

    result = image_agent(state)

    print(result["tool_output"])