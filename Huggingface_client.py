import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()  # This loads both HF_TOKEN and NOVITA_API_KEY

# Use Novita-specific key here
client = InferenceClient(
    provider="novita",
    api_key=os.getenv("NOVITA_API_KEY")
)

def solve_with_openai(question: str, openai_api_key: str = None) -> str:
    """
    Solve question using OpenAI API if available, otherwise fallback to Hugging Face/Novita
    """
    
    # Try OpenAI first if API key is provided
    if openai_api_key:
        try:
            import openai
            openai.api_key = openai_api_key
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if you have access
                messages=[
                    {"role": "system", "content": "You are a helpful homework assistant. Provide clear, educational explanations and step-by-step solutions."},
                    {"role": "user", "content": question}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API failed: {e}")
            print("Falling back to Hugging Face/Novita...")
    
    # Fallback to Hugging Face/Novita
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3-0324",
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: Unable to process your question. {str(e)}"

