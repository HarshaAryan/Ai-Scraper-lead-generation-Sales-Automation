import google.generativeai as genai
from config import settings
import os

# Configure API key
api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in settings or env")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
