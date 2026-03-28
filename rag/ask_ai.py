import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

# -------------------------------
# Load .env from project root
# -------------------------------
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in .env")

# Set environment variable for LangChain/OpenAI
os.environ["OPENAI_API_KEY"] = api_key

# -------------------------------
# Paths
# -------------------------------
VECTOR_PATH = "vector_db"  # FAISS database folder

# -------------------------------
# Function to generate advice
# -------------------------------
def generate_advice(question):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = FAISS.load_local(
        VECTOR_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = vectorstore.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])

    super_prompt = f"""
You are an agricultural expert specialized in greenhouse farming in Mauritius.

Use ONLY the provided context to answer the user's question.

Context:
{context}

Question:
{question}

Provide:
- Explanation of the issue
- Recommended chemical
- Dosage per 20L water
- Withdrawal period
- Practical advice
"""

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise agricultural advisor."},
            {"role": "user", "content": super_prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# -------------------------------
# Continuous question loop
# -------------------------------
if __name__ == "__main__":
    print("🌱 Ask your farming questions. Type 'exit' or 'quit' to stop.")
    while True:
        question = input("\nAsk a farming question: ")
        if question.lower() in ["exit", "quit"]:
            print("Exiting AI assistant. Goodbye!")
            break
        answer = generate_advice(question)
        print("\n===== AI GENERATED ADVICE =====\n")
        print(answer)
