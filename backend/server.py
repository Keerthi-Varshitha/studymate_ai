
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
from rag_engine import answer_question
import requests 

from document_processor import extract_text, split_text

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_DIR = BASE_DIR / "uploaded_files"

UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR),
    static_url_path="/static"
)

CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "txt", "png", "jpg", "jpeg", "webp"
}

# Temporary in-memory storage. No database is used.
document_chunks = []


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"success": True, "message": "Backend is running"})


@app.route("/api/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")

    if not files or all(file.filename == "" for file in files):
        return jsonify({
            "success": False,
            "message": "Please select at least one file."
        }), 400

    processed_files = []
    errors = []

    for file in files:
        if not file.filename:
            continue

        if not allowed_file(file.filename):
            errors.append(f"{file.filename}: Unsupported file type")
            continue

        safe_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        file_path = UPLOAD_DIR / unique_name

        try:
            file.save(file_path)

            text = extract_text(file_path)

            if not text.strip():
                errors.append(f"{safe_name}: No readable text found")
                file_path.unlink(missing_ok=True)
                continue

            chunks = split_text(text)

            for chunk in chunks:
                document_chunks.append({
                    "text": chunk,
                    "source": safe_name
                })

            processed_files.append({
                "name": safe_name,
                "chunks": len(chunks)
            })

        except Exception as error:
            errors.append(f"{safe_name}: {str(error)}")

    return jsonify({
        "success": len(processed_files) > 0,
        "message": "Document processing completed.",
        "processed_files": processed_files,
        "total_chunks": sum(item["chunks"] for item in processed_files),
        "errors": errors
    })



@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({
                "success": False,
                "message": "Please enter a question."
            }), 400

        if not document_chunks:
            return jsonify({
                "success": False,
                "message": "Please upload and process your documents first."
            }), 400

        result = answer_question(question, document_chunks)

        return jsonify({
            "success": True,
            "answer": result["answer"],
            "sources": result["sources"]
        })

    except requests.RequestException as error:
        return jsonify({
            "success": False,
            "message": f"Ollama connection error: {str(error)}"
        }), 503

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500



@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "message": "File is too large. Maximum size is 20 MB."
    }), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
