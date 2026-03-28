import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# -------------------------------
# Load .env from project root
# -------------------------------
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in .env")

# Set it in environment so LangChain can access it
os.environ["OPENAI_API_KEY"] = api_key

# -------------------------------
# Paths
# -------------------------------
DATA_PATH = "../data"       # PDFs folder
VECTOR_PATH = "vector_db"   # Folder to save FAISS vector database

# -------------------------------
# Main function
# -------------------------------
def process_pdfs():
    documents = []

    # Load PDFs
    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            print(f"Loading {file}")
            loader = PyPDFLoader(os.path.join(DATA_PATH, file))
            documents.extend(loader.load())

    if not documents:
        print("No PDFs found in data/ folder.")
        return

    print(f"Loaded {len(documents)} pages")

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    # Create embeddings (will read API key from environment)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Build FAISS vector database
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTOR_PATH)

    print("✅ Vector database created successfully")


# -------------------------------
# Run script
# -------------------------------
if __name__ == "__main__":
    process_pdfs()
