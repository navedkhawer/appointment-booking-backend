import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

async def generate_patient_summary(history_text: str) -> str:
    if not API_KEY:
        print("❌ Error: GEMINI_API_KEY is missing in .env")
        return "AI Service Unavailable: API Key missing."

    try:
        genai.configure(api_key=API_KEY)

        # --- STEP 1: Find a working model automatically ---
        # Instead of guessing 'gemini-pro', we ask the API what we can use.
        valid_model_name = None
        
        # List all models available to your specific API Key
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Prefer the newer, faster models if available
                if 'gemini-1.5-flash' in m.name:
                    valid_model_name = m.name
                    break
                elif 'gemini-pro' in m.name:
                    valid_model_name = m.name
        
        # If we didn't find our favorites, just take the first one that works
        if not valid_model_name:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    valid_model_name = m.name
                    break

        if not valid_model_name:
            print("❌ No text generation models found for this API Key.")
            return "AI Error: No supported models found for your API Key."

        print(f"🤖 Using AI Model: {valid_model_name}")

        # --- STEP 2: Generate Content ---
        model = genai.GenerativeModel(valid_model_name)
        
        prompt = f"""
        You are an expert medical assistant. Analyze the following patient medical history and 
        provide a concise, professional summary for a doctor. 
        Highlight chronic conditions, recent treatments, and recurring patterns.
        
        Patient History:
        {history_text}
        """

        response = model.generate_content(prompt)
        
        if not response.text:
             return "No summary generated (Empty Response)."
             
        return response.text

    except Exception as e:
        print(f"❌ GEMINI API CRITICAL ERROR: {e}")
        return f"AI System Error: {str(e)}"