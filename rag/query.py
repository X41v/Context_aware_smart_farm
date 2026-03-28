import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Load .env from project root
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in .env")
os.environ["OPENAI_API_KEY"] = api_key

VECTOR_PATH = "vector_db"

def query_rag(question):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local(
        VECTOR_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = vectorstore.similarity_search(question, k=3)

    for i, doc in enumerate(docs):
        print(f"\n--- Result {i+1} ---\n")
        print(doc.page_content)

if __name__ == "__main__":
    q = input("Ask a question: ")
    query_rag(q)
