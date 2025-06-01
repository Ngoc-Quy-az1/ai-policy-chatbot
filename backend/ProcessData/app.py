import os
import sys
import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import json

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

def get_db_connection():
    conn = sqlite3.connect('chat_history.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            content TEXT NOT NULL,
            is_bot BOOLEAN NOT NULL,
            timestamp TEXT NOT NULL,
            sources TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        print("Received chat request data:", data)  # Log request data
        question = data.get("question")
        conversation_id = data.get("conversation_id")
        
        if not question:
            print("No question provided in request")
            return jsonify({"error": "No question provided"}), 400

        try:
            print(f"Calling ask_policy_bot with question: {question}")
            # Get the bot's answer
            response = ask_policy_bot(question)
            print("Bot response:", response)  # Log bot response
            
            # Kiểm tra xem có lỗi không
            if isinstance(response, dict) and "error" in response:
                error_msg = response["error"]
                print(f"Error from chatbot: {error_msg}")
                return jsonify({"error": f"Lỗi chatbot: {error_msg}"}), 500
                
            # Lấy câu trả lời từ response
            answer = response.get("answer") if isinstance(response, dict) else None
            if not answer:
                print("No answer received from chatbot")
                return jsonify({"error": "Không nhận được câu trả lời từ chatbot"}), 500

            # Tạo conversation_id mới nếu chưa có
            if not conversation_id:
                conversation_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                conn = get_db_connection()
                conn.execute(
                    'INSERT INTO conversations (id, date) VALUES (?, ?)',
                    (conversation_id, datetime.now().isoformat())
                )
                conn.commit()
                conn.close()

            # Lưu tin nhắn của user
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO messages (conversation_id, content, is_bot, timestamp) VALUES (?, ?, ?, ?)',
                (conversation_id, question, False, datetime.now().isoformat())
            )

            # Lưu tin nhắn của bot
            sources = response.get("sources", {}) if isinstance(response, dict) else {}
            conn.execute(
                'INSERT INTO messages (conversation_id, content, is_bot, timestamp, sources) VALUES (?, ?, ?, ?, ?)',
                (conversation_id, answer, True, datetime.now().isoformat(), json.dumps(sources))
            )
            conn.commit()
            conn.close()

            # Trả về response với đầy đủ thông tin
            return jsonify({
                "answer": answer,
                "sources": sources,
                "conversation_id": conversation_id
            })

        except Exception as bot_error:
            error_msg = str(bot_error)
            print(f"Error from chatbot: {error_msg}")
            
            # Kiểm tra các lỗi phổ biến
            if "OPENAI_API_KEY" in error_msg:
                return jsonify({"error": "Lỗi API key: Vui lòng kiểm tra OPENAI_API_KEY trong file .env"}), 500
            elif "ChromaDB" in error_msg or "vectorstore" in error_msg:
                return jsonify({"error": "Lỗi cơ sở dữ liệu: Vui lòng xử lý file PDF trước khi chat"}), 500
            else:
                return jsonify({"error": f"Lỗi chatbot: {error_msg}"}), 500

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500

@app.route("/api/upload-pdf", methods=["POST"])
def upload_pdf():
    try:
        data = request.json
        file_path = data.get("filePath")
        if not file_path:
            return jsonify({"error": "No file path provided"}), 400
            
        # Kiểm tra file có tồn tại không
        if not os.path.exists(file_path):
            return jsonify({"error": f"File không tồn tại: {file_path}"}), 404
            
        # Kiểm tra file có phải là PDF không
        if not file_path.lower().endswith('.pdf'):
            return jsonify({"error": "File phải có định dạng PDF"}), 400
            
        try:
            result = process_pdf(file_path)
            return jsonify({"message": result})
        except Exception as process_error:
            error_msg = str(process_error)
            print(f"Error processing PDF: {error_msg}")
            
            # Kiểm tra các lỗi phổ biến
            if "JVM" in error_msg or "Java" in error_msg:
                return jsonify({"error": "Lỗi Java: Vui lòng cài đặt Java JDK và thiết lập JAVA_HOME"}), 500
            elif "Tesseract" in error_msg:
                return jsonify({"error": "Lỗi Tesseract: Vui lòng cài đặt Tesseract OCR"}), 500
            elif "Permission denied" in error_msg:
                return jsonify({"error": "Lỗi quyền truy cập: Không thể tạo thư mục hoặc ghi file"}), 500
            else:
                return jsonify({"error": f"Lỗi xử lý PDF: {error_msg}"}), 500
                
    except Exception as e:
        print(f"Error in upload-pdf endpoint: {str(e)}")
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500

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

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    try:
        conn = get_db_connection()
        conversations = conn.execute('''
            SELECT c.id, c.date, m.content as first_message
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id AND m.is_bot = 0
            GROUP BY c.id
            ORDER BY c.date DESC
        ''').fetchall()
        conn.close()

        return jsonify([{
            'id': conv['id'],
            'date': conv['date'],
            'first_message': conv['first_message']
        } for conv in conversations])

    except Exception as e:
        print(f"Error in get_conversations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    try:
        conn = get_db_connection()
        messages = conn.execute('''
            SELECT content, is_bot, timestamp, sources
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        ''', (conversation_id,)).fetchall()
        conn.close()

        return jsonify({
            'messages': [{
                'content': msg['content'],
                'isBot': bool(msg['is_bot']),
                'timestamp': msg['timestamp'],
                'sources': json.loads(msg['sources']) if msg['sources'] else None
            } for msg in messages]
        })

    except Exception as e:
        print(f"Error in get_conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    init_db()
    # Thay đổi cách chạy server để tránh lỗi socket
    app.run(debug=True, use_reloader=False)
