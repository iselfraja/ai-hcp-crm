import requests
import json

base_url = "http://localhost:8000"

print("=" * 60)
print("🧪 Testing All Endpoints")
print("=" * 60)

# 1. Health Check
print("\n1️⃣ Health Check...")
response = requests.get(f"{base_url}/health")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   ✅ {response.json()}")

# 2. Voice Summarization
print("\n2️⃣ Voice Summarization...")
voice_data = {
    "transcript": "Met with Dr. Smith. Discussed Product X. Very positive outcome."
}
response = requests.post(f"{base_url}/voice/summarize", json=voice_data)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"   ✅ Summary: {result.get('summary', '')[:50]}...")
    print(f"   ✅ Sentiment: {result.get('sentiment', 'N/A')}")

# 3. Chat
print("\n3️⃣ Chat Endpoint...")
chat_data = {"message": "Hello, can you help me log a meeting?"}
response = requests.post(f"{base_url}/chat/", json=chat_data)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"   ✅ Reply: {result.get('reply', '')[:50]}...")

print("\n" + "=" * 60)
print("✅ All tests completed!")