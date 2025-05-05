import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import ChatOpenAI    



dotenv_path = r"C:\Users\DELL\OneDrive\Desktop\ai-policy-chatbot\backend\ProcessData\.env"
load_dotenv(dotenv_path=dotenv_path)

def ensure_chroma_dir():
    chroma_dir = "./chroma_db"
    if not os.path.exists(chroma_dir):
        os.makedirs(chroma_dir)
    return chroma_dir

ensure_chroma_dir()

embedding = OpenAIEmbeddings()
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    top_p=1.0,
    temperature=0.5,
    max_tokens=1024,
    frequency_penalty=0.0,
    presence_penalty=0.0
)

memory = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True
)

conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
    ),    
    memory=memory,
    verbose=False
)

def ask_policy_bot(question):
    # Tạo prompt chuẩn
    prompt = f"Bạn là chatbot giúp giải quyết vấn đề hỏi đáp của nhân viên. Hãy trả lời câu hỏi dựa theo tài liệu đã cung cấp. Câu trả lời phải từ khái quát các đề mục tới cụ thể chi tiết. Câu hỏi: {question}"
    
    try:
        response = conversation_chain({"question": prompt})  # Truyền prompt thay vì question gốc
        return response["answer"]
    except Exception as e:
        return f"Lỗi: {str(e)}"


if __name__ == "__main__":
    print("Policy Chatbot đang lắng nghe (gõ 'exit' để thoát):\n")
    while True:
        question = input("Bạn: ")
        if question.lower() in ["exit", "quit"]:
            print("Kết thúc hội thoại.")
            break
        answer = ask_policy_bot(question)
        print("Bot:", answer)
