import os
import traceback

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from workflow import app as langgraph_app


flask_app = Flask(__name__)
flask_app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

UPLOAD_FOLDER = "uploads"
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")

os.makedirs(IMAGE_FOLDER, exist_ok=True)


CHAT_HISTORY = []
MAX_HISTORY_MESSAGES = 6


ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def get_recent_history():
    return CHAT_HISTORY[-MAX_HISTORY_MESSAGES:]


def add_to_history(user_message, assistant_message):
    CHAT_HISTORY.append({
        "user": user_message,
        "assistant": assistant_message
    })

    if len(CHAT_HISTORY) > MAX_HISTORY_MESSAGES:
        del CHAT_HISTORY[:-MAX_HISTORY_MESSAGES]


def get_file_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def is_image(filename):
    return "." in filename and get_file_extension(filename) in ALLOWED_IMAGE_EXTENSIONS


@flask_app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "response": "Uploaded file is too large. Please upload a file below 15 MB."
    }), 413


@flask_app.route("/")
def home():
    return render_template("index.html")


@flask_app.route("/clear", methods=["POST"])
def clear_memory():
    CHAT_HISTORY.clear()

    return jsonify({
        "success": True,
        "response": "Chat memory cleared."
    })


@flask_app.route("/chat", methods=["POST"])
def chat():

    try:

        query = request.form.get("message", "").strip()
        uploaded_file = request.files.get("file")

        file_path = None
        forced_tool = None

        if uploaded_file and uploaded_file.filename:

            filename = secure_filename(uploaded_file.filename)

            if is_image(filename):

                file_path = os.path.join(IMAGE_FOLDER, filename)
                uploaded_file.save(file_path)

                print("\nImage uploaded successfully.")
                print("Image Path:", file_path)

                q = query.lower()

                if any(word in q for word in ["extract", "text", "read", "info", "ocr"]):

                    forced_tool = "ocr"

                    if not query:
                        query = "extract text from this image"

                else:

                    forced_tool = "image"

                    if not query:
                        query = "describe this image"

            else:

                return jsonify({
                    "success": False,
                    "response": "Unsupported file type. Please upload PNG, JPG, JPEG or WEBP."
                }), 400

        if not query:

            return jsonify({
                "success": False,
                "response": "Please enter a question or upload an image."
            }), 400

        state = {
            "query": query,
            "file_path": file_path,
            "forced_tool": forced_tool,
            "history": get_recent_history()
        }

        result = langgraph_app.invoke(state)

        final_response = result.get("response", "No response generated.")

        add_to_history(query, final_response)

        return jsonify({
            "success": True,
            "response": final_response,
            "tool": result.get("tool"),
            "intent": result.get("intent")
        })

    except Exception as e:

        print("\n========== Flask API Error ==========")
        traceback.print_exc()
        print("====================================\n")

        return jsonify({
            "success": False,
            "response": f"Backend error: {str(e)}"
        }), 500


if __name__ == "__main__":
    flask_app.run(debug=True, use_reloader=False)