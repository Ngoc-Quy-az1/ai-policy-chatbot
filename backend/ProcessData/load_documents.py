import os
import sys
import json
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from extract_text import extract_from_pdf, DocumentElement

# Load biến môi trường
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def ensure_chroma_dir():
    chroma_dir = "./chroma_db"
    if not os.path.exists(chroma_dir):
        os.makedirs(chroma_dir)
        print(f" Đã tạo thư mục {chroma_dir}")
    return chroma_dir

def process_text_elements(elements: List[DocumentElement], splitter: RecursiveCharacterTextSplitter) -> List[Document]:
    """Process text elements with appropriate chunking"""
    docs = []
    for element in elements:
        if element.type == 'text':
            texts = splitter.split_text(element.content)
            for text in texts:
                docs.append(Document(
                    page_content=text,
                    metadata={
                        'type': 'text',
                        'page_number': element.page_number,
                        'element_index': elements.index(element)
                    }
                ))
    return docs

def process_table_elements(elements: List[DocumentElement]) -> List[Document]:
    """Process table elements with structured format"""
    docs = []
    for element in elements:
        if element.type == 'table':
            # Convert table to a structured text format
            table_content = element.content
            table_text = f"Table {element.metadata['table_index']}:\n"
            table_text += f"Columns: {', '.join(table_content['columns'])}\n"
            table_text += "Data:\n"
            for row in table_content['data']:
                table_text += f"{json.dumps(row, ensure_ascii=False)}\n"
            
            docs.append(Document(
                page_content=table_text,
                metadata={
                    'type': 'table',
                    'page_number': element.page_number,
                    'table_index': element.metadata['table_index'],
                    'shape': table_content['shape']
                }
            ))
    return docs

def process_chart_elements(elements: List[DocumentElement]) -> List[Document]:
    """Process chart elements with image and text description"""
    docs = []
    for element in elements:
        if element.type == 'chart':
            chart_content = element.content
            chart_text = f"Chart {element.metadata['chart_index']}:\n"
            chart_text += f"Description: {chart_content['text']}\n"
            chart_text += f"Position: {json.dumps(chart_content['position'])}\n"
            chart_text += f"Image saved at: {chart_content['image_path']}"
            
            docs.append(Document(
                page_content=chart_text,
                metadata={
                    'type': 'chart',
                    'page_number': element.page_number,
                    'chart_index': element.metadata['chart_index'],
                    'image_path': chart_content['image_path']
                }
            ))
    return docs

def process_pdf(pdf_path: str) -> str:
    """Process PDF file and store different types of elements in ChromaDB"""
    ensure_chroma_dir()
    
    # Extract all elements from PDF
    elements = extract_from_pdf(pdf_path)
    
    # Initialize text splitter for text content
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    # Process different types of elements
    text_docs = process_text_elements(elements, text_splitter)
    table_docs = process_table_elements(elements)
    chart_docs = process_chart_elements(elements)
    
    # Combine all documents
    all_docs = text_docs + table_docs + chart_docs
    
    # Create embeddings and store in ChromaDB
    embedding = OpenAIEmbeddings(api_key=api_key)
    vectorstore = Chroma.from_documents(
        documents=all_docs,
        embedding=embedding,
        persist_directory="./chroma_db"
    )
    vectorstore.persist()
    
    return f"Đã xử lý và lưu {len(text_docs)} đoạn văn bản, {len(table_docs)} bảng, và {len(chart_docs)} biểu đồ vào ChromaDB."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        result = process_pdf(pdf_path)
        print(result)
    else:
        default_pdf = "ICT205_ASS.pdf"
        if os.path.exists(default_pdf):
            result = process_pdf(default_pdf)
            print(result)
        else:
            print(f"File {default_pdf} không tồn tại. Vui lòng cung cấp đường dẫn đến file PDF.")
