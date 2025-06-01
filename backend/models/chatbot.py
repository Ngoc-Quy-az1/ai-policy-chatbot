import os
import sys
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.schema import Document

dotenv_path = r"C:\Users\DELL\OneDrive\Desktop\ai-policy-chatbot\backend\ProcessData\.env"  
load_dotenv(dotenv_path=dotenv_path)

def ensure_chroma_dir():
    chroma_dir = "./chroma_db"
    if not os.path.exists(chroma_dir):
        os.makedirs(chroma_dir)
    return chroma_dir

ensure_chroma_dir()

# Khởi tạo embedding model
embedding = OpenAIEmbeddings()

# Khởi tạo vectorstore với metadata filtering
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)

# Khởi tạo LLM với các tham số tối ưu cho tốc độ
llm = ChatOpenAI(
    model="gpt-3.5-turbo",  
    temperature=0.1,
    max_tokens=1024,  
    frequency_penalty=0.1,
    presence_penalty=0.1,
    request_timeout=30  # Thêm timeout
)

# Tạo compressor nhẹ hơn
compressor = LLMChainExtractor.from_llm(llm)

# Tạo retriever với contextual compression và số lượng documents ít hơn
base_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 3,  # Giảm số lượng documents để lấy
        "filter": None
    }
)

retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever,
    max_documents=3  # Di chuyển max_documents vào đây
)

# Tạo custom prompt template để hướng dẫn model trả lời chính xác hơn
template = """Bạn là một trợ lý AI chuyên nghiệp, được huấn luyện để trả lời câu hỏi dựa trên tài liệu được cung cấp. Hãy tuân thủ các nguyên tắc sau:

1. Chỉ trả lời dựa trên thông tin có trong context được cung cấp. Nếu không có thông tin đủ để trả lời, hãy nói rõ điều đó.
2. Khi trả lời về bảng số liệu:
   - Trích dẫn chính xác các số liệu từ bảng
   - Nêu rõ nguồn (ví dụ: "Theo Bảng X ở trang Y")
   - Giải thích ý nghĩa của số liệu nếu cần
3. Khi trả lời về biểu đồ:
   - Mô tả xu hướng hoặc mẫu hình chính
   - Trích dẫn các điểm dữ liệu quan trọng
   - Giải thích ý nghĩa của biểu đồ
4. Khi trả lời về công thức:
   - Trích dẫn chính xác công thức từ tài liệu
   - Giải thích ý nghĩa của từng thành phần trong công thức
   - Nêu rõ đơn vị tính (nếu có)
   - Đưa ra ví dụ minh họa cách áp dụng công thức
   - Nếu có nhiều công thức liên quan, hãy giải thích mối quan hệ giữa chúng
5. Cấu trúc câu trả lời:
   - Bắt đầu với thông tin khái quát
   - Sau đó đi vào chi tiết cụ thể
   - Kết thúc với kết luận hoặc tóm tắt nếu phù hợp
6. Nếu có nhiều nguồn thông tin khác nhau, hãy:
   - So sánh và đối chiếu các thông tin
   - Chỉ ra sự khác biệt nếu có
   - Ưu tiên thông tin mới nhất hoặc chính thức nhất

Context: {context}

Chat History: {chat_history}

Câu hỏi: {question}

Hãy trả lời câu hỏi một cách chính xác và đầy đủ:"""

QA_PROMPT = PromptTemplate(
    template=template,
    input_variables=["context", "chat_history", "question"]
)

# Khởi tạo memory với giới hạn token thấp hơn
memory = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="chat_history",
    output_key="answer",
    return_messages=True,
    max_token_limit=1000  # Giảm giới hạn token
)

# Tạo conversation chain với các tham số tối ưu
conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={
        "prompt": QA_PROMPT,
        "document_variable_name": "context"  # Chỉ định rõ tên biến
    },
    verbose=False,  # Tắt verbose để tăng tốc
    return_source_documents=True,
    return_generated_question=True
)

def process_table_context(docs: List[Document]) -> str:
    """Xử lý context từ bảng để tạo mô tả chi tiết hơn"""
    table_contexts = []
    for doc in docs:
        if doc.metadata.get('type') == 'table':
            table_data = doc.page_content
            table_contexts.append(f"Bảng {doc.metadata.get('table_index')} (trang {doc.metadata.get('page_number')}):\n{table_data}")
    return "\n\n".join(table_contexts)

def process_chart_context(docs: List[Document]) -> str:
    """Xử lý context từ biểu đồ để tạo mô tả chi tiết hơn"""
    chart_contexts = []
    for doc in docs:
        if doc.metadata.get('type') == 'chart':
            chart_data = doc.page_content
            chart_contexts.append(f"Biểu đồ {doc.metadata.get('chart_index')} (trang {doc.metadata.get('page_number')}):\n{chart_data}")
    return "\n\n".join(chart_contexts)

def extract_table_number(question: str) -> int:
    """Trích xuất số bảng từ câu hỏi, ví dụ: 'bảng 2' => 2"""
    match = re.search(r"bảng\s*(\d+)", question.lower())
    if match:
        return int(match.group(1))
    return None

def extract_chart_number(question: str) -> int:
    """Trích xuất số biểu đồ từ câu hỏi, ví dụ: 'biểu đồ 3' => 3"""
    match = re.search(r"biểu[\s_-]*đồ\s*(\d+)", question.lower())
    if match:
        return int(match.group(1))
    return None

def extract_formula(question: str) -> bool:
    """Kiểm tra xem câu hỏi có liên quan đến công thức không"""
    formula_keywords = ['công thức', 'formula', 'equation', 'tính', 'toán', 'math']
    return any(keyword in question.lower() for keyword in formula_keywords)

def process_formula_context(docs: List[Document]) -> str:
    """Xử lý context từ công thức để tạo mô tả chi tiết hơn"""
    formula_contexts = []
    for doc in docs:
        if doc.metadata.get('type') == 'formula':
            formula_data = doc.page_content
            formula_contexts.append(f"Công thức (trang {doc.metadata.get('page_number')}):\n{formula_data}")
    return "\n\n".join(formula_contexts)

def ask_policy_bot(question: str) -> Dict[str, Any]:
    """
    Hàm xử lý câu hỏi và trả về câu trả lời cùng với metadata, bảng, công thức hoặc ảnh nếu có
    """
    try:
        is_table_question = 'bảng' in question.lower() or 'số liệu' in question.lower()
        is_chart_question = 'biểu đồ' in question.lower() or 'đồ thị' in question.lower() or 'ảnh' in question.lower() or 'image' in question.lower()
        is_formula_question = extract_formula(question)
        
        table_num = extract_table_number(question) if is_table_question else None
        chart_num = extract_chart_number(question) if is_chart_question else None

        if is_table_question:
            prompt = f"Phân tích bảng số liệu: {question}"
        elif is_chart_question:
            prompt = f"Phân tích biểu đồ: {question}"
        elif is_formula_question:
            prompt = f"Phân tích công thức: {question}"
        else:
            prompt = question

        response = conversation_chain.invoke(
            {"question": prompt},
            timeout=30
        )
        answer = response["answer"]
        source_docs = response.get("source_documents", [])

        # Tìm bảng phù hợp nhất
        table_data = None
        if is_table_question:
            for doc in source_docs:
                if doc.metadata.get('type') == 'table':
                    if table_num is not None:
                        if doc.metadata.get('table_index') == table_num:
                            table_data = doc.page_content
                            break
                    elif table_data is None:
                        table_data = doc.page_content

        # Tìm ảnh biểu đồ phù hợp nhất
        image_path = None
        if is_chart_question:
            for doc in source_docs:
                if doc.metadata.get('type') == 'chart':
                    if chart_num is not None:
                        if doc.metadata.get('chart_index') == chart_num:
                            image_path = doc.metadata.get('image_path')
                            break
                    elif image_path is None:
                        image_path = doc.metadata.get('image_path')

        # Tìm công thức phù hợp nhất
        formula_data = None
        if is_formula_question:
            for doc in source_docs:
                if doc.metadata.get('type') == 'formula':
                    formula_data = doc.page_content
                    break

        result = {
            "answer": answer,
            "table": table_data,
            "image_path": image_path,
            "formula": formula_data,
            "sources": {
                "tables": process_table_context(source_docs),
                "charts": process_chart_context(source_docs),
                "formulas": process_formula_context(source_docs),
                "generated_question": response.get("generated_question", question)
            },
            "metadata": {
                "is_table_question": is_table_question,
                "is_chart_question": is_chart_question,
                "is_formula_question": is_formula_question,
                "num_sources": len(source_docs)
            }
        }
        return result
    except Exception as e:
        print(f"Error in ask_policy_bot: {str(e)}")
        return {
            "answer": "Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi của bạn. Vui lòng thử lại sau.",
            "table": None,
            "image_path": None,
            "formula": None,
            "sources": None,
            "metadata": {"error": str(e)}
        }

if __name__ == "__main__":
    print("Policy Chatbot đang lắng nghe (gõ 'exit' để thoát):\n")
    while True:
        question = input("Bạn: ")
        if question.lower() in ["exit", "quit"]:
            print("Kết thúc hội thoại.")
            break
            
        response = ask_policy_bot(question)
        print("\nBot:", response["answer"])
        
        # In thêm thông tin nếu có
        if response["sources"]:
            if response["sources"]["tables"]:
                print("\nThông tin từ bảng:")
                print(response["sources"]["tables"])
            if response["sources"]["charts"]:
                print("\nThông tin từ biểu đồ:")
                print(response["sources"]["charts"])
            if response["sources"]["formulas"]:
                print("\nThông tin từ công thức:")
                print(response["sources"]["formulas"])
