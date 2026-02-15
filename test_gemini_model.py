"""
Test Gemini API to find the correct model name
"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] No API key found")
        exit(1)
    
    print(f"[OK] API Key found: {api_key[:10]}...")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # List available models
    print("\n[LIST] Available Gemini models:")
    print("-" * 60)
    
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"[OK] {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description[:80]}...")
            print()
    
    # Test with a simple prompt
    print("\n[TEST] Testing model...")
    print("-" * 60)
    
    # Try different model names
    model_names = [
        "gemini-pro",
        "gemini-1.0-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "models/gemini-pro",
        "models/gemini-1.0-pro"
    ]
    
    for model_name in model_names:
        try:
            print(f"\nTrying: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello in one word")
            print(f"[SUCCESS] with {model_name}")
            print(f"   Response: {response.text}")
            print(f"\n[RESULT] Use this model: {model_name}")
            break
        except Exception as e:
            print(f"[FAIL] {str(e)[:100]}")
    
except ImportError:
    print("[ERROR] google-generativeai not installed")
    print("Run: pip install google-generativeai")
except Exception as e:
    print(f"[ERROR] {e}")
