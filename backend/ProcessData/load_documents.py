import os
import sys

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from extract_text import extract_from_pdf

# Load biến môi trường
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Tạo thư mục chroma_db nếu chưa tồn tại
def ensure_chroma_dir():
    chroma_dir = "./chroma_db"
    if not os.path.exists(chroma_dir):
        os.makedirs(chroma_dir)
        print(f" Đã tạo thư mục {chroma_dir}")
    return chroma_dir

def process_pdf(pdf_path):

    ensure_chroma_dir()

    text = extract_from_pdf(pdf_path)



    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_text(text)

    docs = [Document(page_content=t) for t in texts]

    embedding = OpenAIEmbeddings(api_key=api_key)
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory="./chroma_db"
    )
    vectorstore.persist()
    return " Embedding đã lưu vào ChromaDB."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        result = process_pdf(pdf_path)
        print(result)
    else:
        # Nếu không có tham số, sử dụng file ICT205_ASS.pdf mặc định
        default_pdf = "ICT205_ASS.pdf"
        if os.path.exists(default_pdf):
            result = process_pdf(default_pdf)
            print(result)
        else:
            print(f"File {default_pdf} không tồn tại. Vui lòng cung cấp đường dẫn đến file PDF.")
