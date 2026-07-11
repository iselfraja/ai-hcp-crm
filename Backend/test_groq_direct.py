import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print(f"🔑 Testing API key: {api_key[:15] if api_key else 'None'}...")

if not api_key:
    print("❌ No API key found in .env file")
    print("\nPlease add your Groq API key to .env file:")
    print("GROQ_API_KEY=your_api_key_here")
    exit(1)

try:
    client = Groq(api_key=api_key)
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say 'API key is working!'"}],
        temperature=0.3,
        max_tokens=50,
    )
    
    print("✅ Success! API key is valid.")
    print(f"Response: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\n💡 This means your API key is invalid.")
    print("1. Go to https://console.groq.com/keys")
    print("2. Create a NEW API key")
    print("3. Update .env file with the new key")
    print("4. Run this test again")