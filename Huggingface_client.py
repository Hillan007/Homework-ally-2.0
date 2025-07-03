import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()  # This loads both HF_TOKEN and NOVITA_API_KEY

# Use Novita-specific key here
client = InferenceClient(
    provider="novita",
    api_key=os.getenv("NOVITA_API_KEY")
)

def solve_with_openai(question: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3-0324",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content.strip()

