import os
import subprocess
import sys

def setup_project():
    print("🚀 Bắt đầu cài đặt dự án AI Policy Chatbot...")

    # Tạo thư mục chroma_db
    chroma_dir = "./chroma_db"
    if not os.path.exists(chroma_dir):
        os.makedirs(chroma_dir)
        print(f"✅ Đã tạo thư mục {chroma_dir}")
    else:
        print(f"✅ Thư mục {chroma_dir} đã tồn tại")

    # Kiểm tra file .env
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write("OPENAI_API_KEY=your_api_key_here\n")
        print(f"✅ Đã tạo file {env_file}. Vui lòng cập nhật API key của bạn.")
    else:
        print(f"✅ File {env_file} đã tồn tại")

    # Cài đặt các thư viện Python
    print("📦 Đang cài đặt các thư viện Python...")
    try:
        # Cài đặt các thư viện cơ bản từ requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Đã cài đặt các thư viện Python")

        # Cài đặt thêm các thư viện mới
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                               "aiohappyeyeballs==2.4.4", 
                               "aiohttp==3.11.11", 
                               "aiosignal==1.3.2", 
                               "annotated-types==0.7.0", 
                               "anyio==4.8.0", 
                               "asgiref==3.8.1", 
                               "attrs==25.1.0", 
                               "backoff==2.2.1", 
                               "bcrypt==4.2.1", 
                               "blinker==1.9.0", 
                               "chroma-hnswlib==0.7.3", 
                               "chromadb==0.4.22", 
                               "Flask==3.0.2", 
                               "Flask-Cors==4.0.0", 
                               "Flask-SQLAlchemy==3.1.1", 
                               "langchain==0.3.25", 
                               "langchain-community==0.3.23", 
                               "openai==1.77.0", 
                               "pdfplumber==0.10.3", 
                               "python-dotenv==1.0.1", 
                               "tiktoken==0.9.0"])
        print("✅ Đã cài đặt các thư viện mới")
    except subprocess.CalledProcessError:
        print("❌ Lỗi khi cài đặt các thư viện Python")
        return False

    # Kiểm tra file ICT205_ASS.pdf
    pdf_file = "ICT205_ASS.pdf"
    if not os.path.exists(pdf_file):
        print(f"⚠️ File {pdf_file} không tồn tại. Vui lòng đảm bảo file này tồn tại trong thư mục gốc.")
    else:
        print(f"✅ File {pdf_file} đã tồn tại")

    print("\n🎉 Cài đặt hoàn tất! Bạn có thể chạy ứng dụng bằng cách:")
    print("1. Cập nhật API key trong file .env")
    print("2. Chạy backend: python app.py")
    print("3. Chạy frontend: cd client && npm start")

    return True

if __name__ == "__main__":
    setup_project()
