import os

print("=" * 50)
print("🔑 How to Create a New Groq API Key")
print("=" * 50)

print("""
1. Open your browser and go to:
   https://console.groq.com/keys

2. Log in to your Groq account

3. Click the 'Create API Key' button

4. Enter a name: hcp-crm

5. Click 'Create'

6. COPY THE API KEY IMMEDIATELY!
   You won't see it again after you close the page

7. Open your .env file and update the GROQ_API_KEY line:
   GROQ_API_KEY=your_new_key_here

8. Save the .env file

9. Run: python test_groq_direct.py
""")

print("\n⚠️ IMPORTANT:")
print("   - The key starts with 'gsk_'")
print("   - No spaces, no quotes around the key")
print("   - Save the file after adding the key")
print("=" * 50)