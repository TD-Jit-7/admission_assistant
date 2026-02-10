from google import genai
from google.genai import types

# Your API key
GEMINI_API_KEY = "AIzaSyCoZd1akvhUZViGcmfTkOlL10HsnhUVJJo"

try:
    
    client = genai.Client(api_key=GEMINI_API_KEY)  
    response = client.models.generate_content(model='gemini-3-flash-preview', contents = "Hello, test message")
    print("✅ SUCCESS! API Key is working!")
    print("Response:", response.text)
    
except Exception as e:
    print("❌ ERROR! API Key is NOT working!")
    print("Error message:", str(e))