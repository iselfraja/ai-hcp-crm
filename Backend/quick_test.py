from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ No API key found")
    exit(1)

print("Testing with Groq SDK...")

try:
    from groq import Groq
    client = Groq(api_key=api_key)
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say hello"}],
        temperature=0.3,
        max_tokens=20,
    )
    
    print("✅ SUCCESS!")
    print(f"Response: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")