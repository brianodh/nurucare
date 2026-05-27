"""
NuruCare - Google Gemini AI Client
Handles AI-powered recommendations and Swahili translation
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDmKcAubUrtNIrKk9x7DBqr8mvKvf0m5cw")
genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 1.5 Flash (fast and efficient)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_recommendation(user_data: dict) -> str:
    """
    Get personalized contraceptive recommendation from Gemini AI
    """
    prompt = f"""
    You are a compassionate contraceptive counselor for women in Sub-Saharan Africa.
    
    User profile:
    - Age: {user_data.get('age')}
    - Has children: {user_data.get('parity', 0)}
    - Wants children in future: {user_data.get('fertility_intention')}
    - Smokes: {user_data.get('smoking', False)}
    - Breastfeeding: {user_data.get('breastfeeding', False)}
    - Has migraines: {user_data.get('migraine_type')}
    
    Based on WHO Medical Eligibility Criteria (MEC), recommend 2-3 contraceptive methods.
    For each method, explain:
    1. Why it's suitable for this person
    2. Effectiveness percentage
    3. Common side effects
    4. One myth vs fact
    
    Keep response clear, helpful, and culturally sensitive.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Unable to generate recommendation at this time. Please consult a healthcare provider."

def translate_to_swahili(text: str) -> str:
    """
    Translate English text to Swahili for multilingual support
    """
    prompt = f"""
    Translate the following contraceptive health information from English to Swahili.
    Use simple, clear Swahili that a young woman can understand.
    Keep medical terms accurate.
    
    Text to translate: {text}
    
    Swahili translation:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original if translation fails

def get_myth_busting(method_name: str) -> str:
    """
    Get myth vs fact for a specific contraceptive method
    """
    prompt = f"""
    Provide one common myth and the corresponding fact about {method_name}.
    
    Format:
    Myth: [the myth]
    Fact: [the truth]
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Myth: {method_name} causes infertility. Fact: {method_name} does not affect future fertility."

# Test the AI client
if __name__ == "__main__":
    test_user = {
        "age": 28,
        "parity": 1,
        "fertility_intention": "long_term",
        "smoking": False,
        "breastfeeding": False,
        "migraine_type": "none"
    }
    
    print("Testing AI Recommendation:")
    print(get_ai_recommendation(test_user))
    print("\n" + "="*50 + "\n")
    
    print("Testing Swahili Translation:")
    print(translate_to_swahili("Use condoms to prevent pregnancy and sexually transmitted infections."))