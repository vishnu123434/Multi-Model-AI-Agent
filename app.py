"""
app.py

Flask API for Multi-Model AI Agent

Handles:
1. Text queries
2. Document uploads: PDF, DOCX, TXT
3. Image uploads
4. LangGraph workflow execution
"""

import os
import traceback

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from workflow import app as langgraph_app
from tools.document_loader import ingest_document


# ------------------------------------
# Flask App Setup
# ------------------------------------

flask_app = Flask(__name__)

# Maximum upload size: 15 MB
flask_app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

UPLOAD_FOLDER = "uploads"
DOCUMENT_FOLDER = os.path.join(UPLOAD_FOLDER, "documents")
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")

os.makedirs(DOCUMENT_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)


# ------------------------------------
# Allowed Files
# ------------------------------------

ALLOWED_DOCUMENT_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def get_file_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def is_document(filename):
    return "." in filename and get_file_extension(filename) in ALLOWED_DOCUMENT_EXTENSIONS


def is_image(filename):
    return "." in filename and get_file_extension(filename) in ALLOWED_IMAGE_EXTENSIONS


# ------------------------------------
# Error Handler
# ------------------------------------

@flask_app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "response": "Uploaded file is too large. Please upload a file below 15 MB."
    }), 413


# ------------------------------------
# Home Route
# ------------------------------------

@flask_app.route("/")
def home():
    return render_template("index.html")


# ------------------------------------
# Chat API Route
# ------------------------------------

@flask_app.route("/chat", methods=["POST"])
def chat():

    try:
        query = request.form.get("message", "").strip()
        uploaded_file = request.files.get("file")

        file_path = None

        # ------------------------------------
        # Handle Uploaded File
        # ------------------------------------

        if uploaded_file and uploaded_file.filename:

            filename = secure_filename(uploaded_file.filename)

            if is_document(filename):

                file_path = os.path.join(DOCUMENT_FOLDER, filename)

                uploaded_file.save(file_path)

                print("\nDocument uploaded successfully.")
                print(f"Document Path: {file_path}")

                ingest_document(file_path)

                if not query:
                    query = "Summarize this document"

            elif is_image(filename):

                file_path = os.path.join(IMAGE_FOLDER, filename)

                uploaded_file.save(file_path)

                print("\nImage uploaded successfully.")
                print(f"Image Path: {file_path}")

                if not query:
                    query = "Describe this image"

            else:

                return jsonify({
                    "success": False,
                    "response": "Unsupported file type. Please upload PDF, DOCX, TXT, PNG, JPG, JPEG, or WEBP."
                }), 400

        # ------------------------------------
        # Validate Query
        # ------------------------------------

        if not query:

            return jsonify({
                "success": False,
                "response": "Please enter a question or upload a file."
            }), 400

        # ------------------------------------
        # LangGraph State
        # ------------------------------------

        state = {
            "query": query,
            "file_path": file_path,
            "history": []
        }

        # ------------------------------------
        # Run LangGraph Workflow
        # ------------------------------------

        result = langgraph_app.invoke(state)

        final_response = result.get(
            "response",
            "No response generated."
        )

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


# ------------------------------------
# Run App
# ------------------------------------

if __name__ == "__main__":

    flask_app.run(
        debug=True,
        use_reloader=False
    )