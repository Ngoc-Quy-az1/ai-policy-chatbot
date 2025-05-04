import os
import sys
import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

sys.path.append(os.path.abspath("../models"))
sys.path.append(os.path.abspath("../ProcessData"))

from chatbot import ask_policy_bot
from load_documents import process_pdf

# Khởi tạo Flask và SQLAlchemy
app = Flask(__name__)
CORS(app)

# Cấu hình cơ sở dữ liệu SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mô hình lưu trữ tin nhắn
class MessageHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(100), nullable=False)
    user_message = db.Column(db.String(500), nullable=False)
    bot_response = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Khởi tạo cơ sở dữ liệu (nếu chưa có)
with app.app_context():
    db.create_all()

# Hàm tạo conversation_id ngẫu nhiên
def generate_conversation_id():
    today = datetime.utcnow().strftime('%Y-%m-%d')
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{today}_{random_str}"

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        question = data.get("message")
        if not question:
            return jsonify({"error": "No question provided"}), 400

        # Get the bot's answer
        answer = ask_policy_bot(question)

        # Generate conversation_id for today's date
        conversation_id = datetime.utcnow().strftime('%Y-%m-%d')

        # Save the new message in the database
        new_message = MessageHistory(conversation_id=conversation_id, user_message=question, bot_response=answer)
        db.session.add(new_message)
        db.session.commit()

        # Retrieve all messages grouped by date
        all_messages = MessageHistory.query.order_by(MessageHistory.timestamp).all()
        grouped_messages = {}

        for msg in all_messages:
            date = msg.conversation_id
            if date not in grouped_messages:
                grouped_messages[date] = []
            grouped_messages[date].append({
                'user_message': msg.user_message,
                'bot_response': msg.bot_response,
                'timestamp': msg.timestamp
            })

        return jsonify({"response": answer, "messages": grouped_messages})

    except Exception as e:
        print(f"Error: {str(e)}")
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
        print(f"Error: {str(e)}")  # In ra lỗi chi tiết
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
        print(f"Error: {str(e)}")  # In ra lỗi chi tiết
        return jsonify({"error": str(e)}), 500

@app.route("/api/message-history", methods=["GET"])
def message_history():
    try:
        date_str = request.args.get("date")  

        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                start = datetime.combine(date_obj, datetime.min.time())
                end = datetime.combine(date_obj, datetime.max.time())

                messages = MessageHistory.query.filter(
                    MessageHistory.timestamp.between(start, end)
                ).order_by(MessageHistory.timestamp).all()

                result = [
                    {
                        "conversation_id": msg.conversation_id,
                        "user_message": msg.user_message,
                        "bot_response": msg.bot_response,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in messages
                ]
                return jsonify(result)
            except ValueError:
                return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
        else:
            # Mặc định: trả về tất cả
            conversations = db.session.query(MessageHistory.conversation_id).distinct().all()
            conversation_list = []

            for conversation in conversations:
                conversation_id = conversation[0]
                messages = MessageHistory.query.filter_by(conversation_id=conversation_id).order_by(MessageHistory.timestamp).all()
                message_list = [
                    {"user_message": msg.user_message, "bot_response": msg.bot_response, "timestamp": msg.timestamp}
                    for msg in messages
                ]
                conversation_list.append({"conversation_id": conversation_id, "messages": message_list})

            return jsonify(conversation_list)

    except Exception as e:
        print(f"Error: {str(e)}")  # In ra lỗi chi tiết
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
