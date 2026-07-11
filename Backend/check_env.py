import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

print("=" * 50)
print("🔍 Environment Variables Check")
print("=" * 50)

print(f"\nGROQ_API_KEY: '{api_key}'")
print(f"Length: {len(api_key) if api_key else 0} characters")
print(f"Starts with 'gsk_': {api_key.startswith('gsk_') if api_key else False}")
print(f"Contains spaces: {' ' in api_key if api_key else False}")

if api_key and api_key.startswith('"'):
    print("⚠️ API key has quotes - please remove them")

print(f"\nGROQ_MODEL: {model or 'Not set'}")

print("\n" + "=" * 50)
print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")