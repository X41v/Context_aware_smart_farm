from flask import Blueprint, request, jsonify
import subprocess
import socket
from config import BASE_DIR
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

ai_bp = Blueprint("ai", __name__)

# Load vector DB
print("Loading AI vector database...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.load_local(
    str(BASE_DIR / "rag" / "vector_db"),
    embeddings,
    allow_dangerous_deserialization=True
)
client = OpenAI()
print("✅ AI system ready")

OLLAMA_MODEL = "tinyllama"

def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

@ai_bp.route("/ask-ai", methods=["POST"])
def ask_ai():
    data = request.json
    question = data.get("question")
    farm_type = data.get("farm_type", "soil")

    if not question:
        return jsonify({"response": "No question provided"}), 400

    use_online = check_internet()

    if use_online:
        try:
            docs = vectorstore.similarity_search(question, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])
            prompt = f"""
You are an agricultural expert specialized in {farm_type} farming.

Context:
{context}

Question:
{question}

Provide:
- Explanation
- Recommended chemical
- Dosage per 20L water
- Withdrawal period
- Practical advice
"""
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are a precise {farm_type} advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return jsonify({"response": response.choices[0].message.content})
        except Exception as e:
            print(f"⚠ Online AI error: {e}")

    # Offline fallback
    try:
        offline_prompt = f"""
You are an agricultural expert specialized in {farm_type} farming.

Question:
{question}

Provide:
- Explanation
- Recommended chemical
- Dosage per 20L water
- Withdrawal period
- Practical advice
"""
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL, offline_prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        response_text = result.stdout.strip() or "TinyLlama did not return any answer."
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"TinyLlama offline error: {str(e)}"})
