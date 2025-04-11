import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Load biến môi trường từ file .env
load_dotenv()

# Tạo thư mục chroma_db nếu chưa tồn tại
def ensure_chroma_dir():
    chroma_dir = "./chroma_db"
    if not os.path.exists(chroma_dir):
        os.makedirs(chroma_dir)
        print(f"✅ Đã tạo thư mục {chroma_dir}")
    return chroma_dir

ensure_chroma_dir()

embedding = OpenAIEmbeddings()
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=OpenAI(temperature=0),
    retriever=vectorstore.as_retriever(),
    memory=memory,
    verbose=True
)

# Hỏi bot
def ask_policy_bot(question):
    try:
        response = conversation_chain({"question": question})
        return response["answer"]
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = sys.argv[1]
        answer = ask_policy_bot(question)
        print(answer)
    else:
        print("Please provide a question as argument")
