import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load the API key from your .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Attempting to list available models...")

try:
    # This script will list all models your API key can access
    for m in genai.list_models():
        # We only care about the models that support the 'generateContent' method
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"\nAn error occurred: {e}")

print("\nTest finished.")