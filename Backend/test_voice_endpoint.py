# backend/test_voice_endpoint.py
import requests

url = "http://localhost:8000/voice/summarize"
data = {
    "transcript": "Met with Dr. Sharma today. Discussed Product X efficacy. The doctor was very positive about the results and requested the Phase III study brochure. We should follow up in two weeks."
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Summary generated successfully!")
        print(f"Summary: {result.get('summary', 'N/A')}")
        print(f"Sentiment: {result.get('sentiment', 'N/A')}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Connection error: {str(e)}")