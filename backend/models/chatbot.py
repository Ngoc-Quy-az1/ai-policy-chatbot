import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory

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

llm = OpenAI(temperature=0)

memory = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True
)

conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory,
    verbose=True
)

def ask_policy_bot(question):
    try:
        response = conversation_chain({"question": question})
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
