import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyCoZd1akvhUZViGcmfTkOlL10HsnhUVJJo"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    
    print("📋 Available Models:\n")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
    
except Exception as e:
    print(f"❌ Error: {e}")