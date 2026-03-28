from dotenv import load_dotenv
import os
from openai import OpenAI

# Force load .env file
load_dotenv(".env")

# Debug (IMPORTANT - remove later)
print("API KEY:", os.getenv("OPENAI_API_KEY")[:10], "...")

client = OpenAI()

while True:
    question = input("You: ")

    if question.lower() == "exit":
        break

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}]
    )

    print("AI:", response.choices[0].message.content)
