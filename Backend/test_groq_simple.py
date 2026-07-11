# backend/test_groq_direct.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print(f"🔑 Testing API key: {api_key[:15]}...")

if not api_key:
    print("❌ No API key found")
    exit(1)

try:
    client = Groq(api_key=api_key)
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say hello"}],
        temperature=0.3,
        max_tokens=50,
    )
    
    print("✅ Success!")
    print(f"Response: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")