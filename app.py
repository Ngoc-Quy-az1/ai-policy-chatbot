from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import ask_policy_bot
from load_documents import process_pdf
import os

app = Flask(__name__)
CORS(app)  

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        question = data.get("message")
        if not question:
            return jsonify({"error": "No question provided"}), 400
            
        answer = ask_policy_bot(question)
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/upload-pdf", methods=["POST"])
def upload_pdf():
    try:
        data = request.json
        file_path = data.get("filePath")
        if not file_path:
            return jsonify({"error": "No file path provided"}), 400
            
        result = process_pdf(file_path)
        return jsonify({"message": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/process-default", methods=["POST"])
def process_default():
    try:
        default_pdf = "ICT205_ASS.pdf"
        if os.path.exists(default_pdf):
            result = process_pdf(default_pdf)
            return jsonify({"message": result})
        else:
            return jsonify({"error": f"File {default_pdf} không tồn tại"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
