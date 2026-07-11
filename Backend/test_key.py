import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print(f"🔑 Testing API key: {api_key[:15] if api_key else 'None'}...")

if not api_key:
    print("❌ No API key found")
    exit(1)

try:
    client = Groq(api_key=api_key)
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say 'It works!'"}],
        temperature=0.3,
        max_tokens=30,
    )
    
    print("✅ SUCCESS! API key is valid.")
    print(f"Response: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\n💡 Your API key is still invalid.")
    print("1. Go to https://console.groq.com/keys")
    print("2. Create a NEW API key")
    print("3. Update .env with the new key")