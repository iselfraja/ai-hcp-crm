# backend/test_chat_endpoint.py
import requests

url = "http://localhost:8000/chat/"
data = {"message": "Hello, can you help me log a meeting with Dr. Smith?"}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Reply: {result.get('reply', 'N/A')}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")