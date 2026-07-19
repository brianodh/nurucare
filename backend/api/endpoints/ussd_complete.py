"""
NuruCare - Complete USSD Handler with All Questions
====================================================

This module provides a clean, structured implementation of the USSD flow
with all intake questions, session management, and AI integration.

USSD Flow:
0. Welcome → 1. Terms → 2. Age → 3. Relationship → 4. Systolic BP
5. Diastolic BP → 6. Smoking → 7. Migraine → 8. LMP → 9. Cycle Length
10. Irregular Periods → 11. Fertility Intent → 12. Breastfeeding
13. Side Effects → 14. Processing → 15. Results → 16. Method Details

Author: Brian Odhiambo Ouma
Date: July 2026
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

# Import session manager and recommendation pipeline
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ussd.session_manager import get_session_manager
from engine.recommendation_pipeline import RecommendationPipeline

# Initialize router
router = APIRouter(prefix="/ussd-complete", tags=["USSD Complete"])

# Initialize session manager
session_manager = get_session_manager()

# Initialize recommendation pipeline (lazy loading)
_pipeline = None

def get_pipeline():
    """Lazy load the recommendation pipeline"""
    global _pipeline
    if _pipeline is None:
        _pipeline = RecommendationPipeline()
    return _pipeline


# ============================================
# DATA MODELS
# ============================================

class USSDRequest(BaseModel):
    """Africa's Talking USSD request format"""
    sessionId: str
    serviceCode: str
    phoneNumber: str
    text: str


class USSDResponse:
    """Helper for USSD responses"""
    
    @staticmethod
    def con(message: str) -> dict:
        """Continue session"""
        return {"text": message, "type": "con"}
    
    @staticmethod
    def end(message: str) -> dict:
        """End session"""
        return {"text": message, "type": "end"}
    
    @staticmethod
    def release(message: str) -> dict:
        """Release session (end with message)"""
        return {"text": message, "type": "end"}


# ============================================
# COMPLETE USSD INTAKE FLOW
# ============================================

class USSDIntakeFlow:
    """
    Complete USSD intake flow with all questions.
    
    Map of question order:
    0: welcome        - Welcome screen
    1: terms          - Terms and Conditions
    2: age            - User's age
    3: relationship   - Relationship status
    4: bp_systolic    - Systolic blood pressure
    5: bp_diastolic   - Diastolic blood pressure
    6: smoking        - Smoking status
    7: migraine       - Migraine type
    8: lmp            - Last Menstrual Period
    9: cycle_length   - Cycle length in days
    10: irregular     - Irregular periods
    11: fertility     - Fertility intentions
    12: breastfeeding - Breastfeeding status
    13: side_effects  - Side effects to avoid
    14: processing    - Processing/Analyzing
    15: results       - Show recommendations
    16: method_details - Method details
    """
    
    QUESTIONS = [
        "welcome",        # 0
        "terms",          # 1
        "age",            # 2
        "relationship",   # 3
        "bp_systolic",    # 4
        "bp_diastolic",   # 5
        "smoking",        # 6
        "migraine",       # 7
        "lmp",            # 8
        "cycle_length",   # 9
        "irregular",      # 10
        "fertility",      # 11
        "breastfeeding",  # 12
        "side_effects",   # 13
        "processing",     # 14
        "results"         # 15
    ]
    
    def __init__(self):
        self.pipeline = get_pipeline()
    
    async def handle(self, session_id: str, user_input: str, current_step: int):
        """
        Handle each step of the USSD flow.
        
        Args:
            session_id: Unique session identifier
            user_input: User's latest input (single response)
            current_step: Current step number
            
        Returns:
            USSDResponse with the next menu or end message
        """
        
        # Store the user's phone number if not already stored
        phone = session_manager.get_phone_number(session_id)
        if phone is None:
            # Phone number will be set in the main callback
            pass
        
        if current_step == 0:
            return self._welcome()
        
        elif current_step == 1:
            return self._terms(user_input, session_id)
        
        elif current_step == 2:
            return self._age(user_input, session_id)
        
        elif current_step == 3:
            return self._relationship(user_input, session_id)
        
        elif current_step == 4:
            return self._bp_systolic(user_input, session_id)
        
        elif current_step == 5:
            return self._bp_diastolic(user_input, session_id)
        
        elif current_step == 6:
            return self._smoking(user_input, session_id)
        
        elif current_step == 7:
            return self._migraine(user_input, session_id)
        
        elif current_step == 8:
            return self._lmp(user_input, session_id)
        
        elif current_step == 9:
            return self._cycle_length(user_input, session_id)
        
        elif current_step == 10:
            return self._irregular(user_input, session_id)
        
        elif current_step == 11:
            return self._fertility(user_input, session_id)
        
        elif current_step == 12:
            return self._breastfeeding(user_input, session_id)
        
        elif current_step == 13:
            return self._side_effects(user_input, session_id)
        
        elif current_step == 14:
            return await self._processing(session_id)
        
        elif current_step == 15:
            return await self._results(user_input, session_id)
        
        else:
            # Unknown step - end session
            session_manager.delete_session(session_id)
            return USSDResponse.end("Session expired. Please dial *384*123# again.")
    
    # --- Step 0: Welcome ---
    def _welcome(self) -> dict:
        return USSDResponse.con(
            "Welcome to NuruCare - AI Contraceptive Support\n\n"
            "1. Continue\n"
            "2. Cancel\n\n"
            "Reply with 1 to continue"
        )
    
    # --- Step 1: Terms and Conditions ---
    def _terms(self, user_input: str, session_id: str) -> dict:
        if user_input == "1":
            session_manager.set_step(session_id, 2)
            return USSDResponse.con(
                "Terms & Conditions\n\n"
                "By continuing, you agree to our Terms & Privacy Policy.\n"
                "Your data is encrypted and never shared.\n\n"
                "1. I agree\n"
                "2. I do not agree\n\n"
                "Reply with 1 to continue"
            )
        elif user_input == "2":
            session_manager.delete_session(session_id)
            return USSDResponse.end("Thank you for using NuruCare. Goodbye.")
        else:
            return USSDResponse.con(
                "Please reply with 1 to continue or 2 to cancel."
            )
    
    # --- Step 2: Age ---
    def _age(self, user_input: str, session_id: str) -> dict:
        try:
            age = int(user_input)
            if 15 <= age <= 49:
                session_manager.update_session(session_id, {"age": age})
                session_manager.set_step(session_id, 3)
                return USSDResponse.con(
                    "Relationship Status\n\n"
                    "1. Single\n"
                    "2. In a relationship\n"
                    "3. Married\n"
                    "4. Prefer not to say\n\n"
                    "Reply with 1-4"
                )
            return USSDResponse.con("Invalid age. Please enter 15-49.")
        except ValueError:
            return USSDResponse.con("Please enter your age (e.g., 28)")
    
    # --- Step 3: Relationship Status ---
    def _relationship(self, user_input: str, session_id: str) -> dict:
        mapping = {
            "1": "Single",
            "2": "In a relationship",
            "3": "Married",
            "4": "Prefer not to say"
        }
        if user_input in mapping:
            session_manager.update_session(session_id, {"relationship": mapping[user_input]})
            session_manager.set_step(session_id, 4)
            return USSDResponse.con(
                "Enter Systolic Blood Pressure (top number):\n\n"
                "e.g., 120\n\n"
                "Reply with a number"
            )
        return USSDResponse.con("Please reply with 1-4")
    
    # --- Step 4: Systolic BP ---
    def _bp_systolic(self, user_input: str, session_id: str) -> dict:
        try:
            bp = int(user_input)
            if 60 <= bp <= 200:
                session_manager.update_session(session_id, {"systolic_bp": bp})
                session_manager.set_step(session_id, 5)
                return USSDResponse.con(
                    "Enter Diastolic Blood Pressure (bottom number):\n\n"
                    "e.g., 80\n\n"
                    "Reply with a number"
                )
            return USSDResponse.con("Invalid systolic BP. Enter 60-200.")
        except ValueError:
            return USSDResponse.con("Please enter a valid number (e.g., 120)")
    
    # --- Step 5: Diastolic BP ---
    def _bp_diastolic(self, user_input: str, session_id: str) -> dict:
        try:
            bp = int(user_input)
            if 40 <= bp <= 120:
                session_manager.update_session(session_id, {"diastolic_bp": bp})
                session_manager.set_step(session_id, 6)
                return USSDResponse.con(
                    "Do you currently smoke?\n\n"
                    "1. Yes\n"
                    "2. No\n\n"
                    "Reply with 1 or 2"
                )
            return USSDResponse.con("Invalid diastolic BP. Enter 40-120.")
        except ValueError:
            return USSDResponse.con("Please enter a valid number (e.g., 80)")
    
    # --- Step 6: Smoking Status ---
    def _smoking(self, user_input: str, session_id: str) -> dict:
        mapping = {"1": True, "2": False}
        if user_input in mapping:
            session_manager.update_session(session_id, {"smoking": mapping[user_input]})
            session_manager.set_step(session_id, 7)
            return USSDResponse.con(
                "Do you have migraines?\n\n"
                "1. No migraines\n"
                "2. Migraine without aura\n"
                "3. Migraine with aura\n\n"
                "Reply with 1-3"
            )
        return USSDResponse.con("Please reply with 1 or 2")
    
    # --- Step 7: Migraine Type ---
    def _migraine(self, user_input: str, session_id: str) -> dict:
        mapping = {
            "1": "none",
            "2": "without_aura",
            "3": "with_aura"
        }
        if user_input in mapping:
            session_manager.update_session(session_id, {"migraine_type": mapping[user_input]})
            session_manager.set_step(session_id, 8)
            return USSDResponse.con(
                "When was your last menstrual period?\n\n"
                "Format: DDMMYYYY\n"
                "e.g., 11072026\n\n"
                "Reply with date"
            )
        return USSDResponse.con("Please reply with 1-3")
    
    # --- Step 8: Last Menstrual Period ---
    def _lmp(self, user_input: str, session_id: str) -> dict:
        if len(user_input) == 8 and user_input.isdigit():
            day = int(user_input[:2])
            month = int(user_input[2:4])
            year = int(user_input[4:8])
            if 1 <= day <= 31 and 1 <= month <= 12 and 2000 <= year <= 2030:
                session_manager.update_session(session_id, {"lmp": user_input})
                session_manager.set_step(session_id, 9)
                return USSDResponse.con(
                    "How many days is your typical cycle?\n\n"
                    "e.g., 28\n\n"
                    "Reply with number"
                )
        return USSDResponse.con("Invalid format. Use DDMMYYYY (e.g., 11072026)")
    
    # --- Step 9: Cycle Length ---
    def _cycle_length(self, user_input: str, session_id: str) -> dict:
        try:
            days = int(user_input)
            if 20 <= days <= 45:
                session_manager.update_session(session_id, {"cycle_length": days})
                session_manager.set_step(session_id, 10)
                return USSDResponse.con(
                    "Do you have irregular periods?\n\n"
                    "1. No\n"
                    "2. Yes, irregular\n"
                    "3. Suspected hormonal imbalance\n\n"
                    "Reply with 1-3"
                )
            return USSDResponse.con("Enter 20-45 days.")
        except ValueError:
            return USSDResponse.con("Please enter a number (e.g., 28)")
    
    # --- Step 10: Irregular Periods ---
    def _irregular(self, user_input: str, session_id: str) -> dict:
        mapping = {
            "1": "No",
            "2": "Yes, irregular",
            "3": "Suspected hormonal imbalance"
        }
        if user_input in mapping:
            session_manager.update_session(session_id, {"irregular_periods": mapping[user_input]})
            session_manager.set_step(session_id, 11)
            return USSDResponse.con(
                "When do you want to have children?\n\n"
                "1. Within 1 year\n"
                "2. In 1-5 years\n"
                "3. No more children (long-term)\n"
                "4. Unsure\n\n"
                "Reply with 1-4"
            )
        return USSDResponse.con("Please reply with 1-3")
    
    # --- Step 11: Fertility Intentions ---
    def _fertility(self, user_input: str, session_id: str) -> dict:
        mapping = {
            "1": "want_soon",
            "2": "want_later",
            "3": "no_more",
            "4": "unsure"
        }
        if user_input in mapping:
            session_manager.update_session(session_id, {"fertility_intent": mapping[user_input]})
            session_manager.set_step(session_id, 12)
            return USSDResponse.con(
                "Are you currently breastfeeding?\n\n"
                "1. Yes\n"
                "2. No\n\n"
                "Reply with 1 or 2"
            )
        return USSDResponse.con("Please reply with 1-4")
    
    # --- Step 12: Breastfeeding ---
    def _breastfeeding(self, user_input: str, session_id: str) -> dict:
        mapping = {"1": True, "2": False}
        if user_input in mapping:
            session_manager.update_session(session_id, {"breastfeeding": mapping[user_input]})
            session_manager.set_step(session_id, 13)
            return USSDResponse.con(
                "Select side effects you want to avoid:\n\n"
                "1. Weight gain\n"
                "2. Mood shifts\n"
                "3. Acne\n"
                "4. Irregular bleeding\n"
                "5. Low libido\n"
                "6. None\n\n"
                "Reply with numbers separated by commas\n"
                "e.g., 1,3,5"
            )
        return USSDResponse.con("Please reply with 1 or 2")
    
    # --- Step 13: Side Effects to Avoid ---
    def _side_effects(self, user_input: str, session_id: str) -> dict:
        side_effect_map = {
            "1": "weight_gain",
            "2": "mood_shifts",
            "3": "acne",
            "4": "irregular_bleeding",
            "5": "low_libido",
            "6": "none"
        }
        
        try:
            selected = []
            for item in user_input.split(','):
                item = item.strip()
                if item in side_effect_map:
                    selected.append(side_effect_map[item])
            
            if selected:
                session_manager.update_session(session_id, {"side_effect_concerns": selected})
                session_manager.set_step(session_id, 14)
                return USSDResponse.con(
                    "Processing your information...\n\n"
                    "Please wait"
                )
        except:
            pass
        
        return USSDResponse.con(
            "Invalid input. Use numbers separated by commas.\n"
            "e.g., 1,3,5"
        )
    
    # --- Step 14: Processing (Generate Recommendations) ---
    async def _processing(self, session_id: str) -> dict:
        # Get all collected data
        data = session_manager.get_data(session_id)
        
        # Build the user profile for the AI engine
        profile = {
            "age": data.get("age", 0),
            "smoking": data.get("smoking", False),
            "migraine_type": data.get("migraine_type", "none"),
            "systolic_bp": data.get("systolic_bp", 0),
            "diastolic_bp": data.get("diastolic_bp", 0),
            "breastfeeding": data.get("breastfeeding", False),
            "postpartum_weeks": 100,  # Default (not recently postpartum)
            "fertility_intent": data.get("fertility_intent", "unsure"),
            "cycle_regularity": "regular" if data.get("irregular_periods") == "No" else "irregular"
        }
        
        # Store profile in session for results
        session_manager.update_session(session_id, {"profile": profile})
        session_manager.set_step(session_id, 15)
        
        return USSDResponse.con(
            "Analyzing your profile...\n\n"
            "Your results are ready!"
        )
    
    # --- Step 15: Results ---
    async def _results(self, user_input: str, session_id: str) -> dict:
        data = session_manager.get_data(session_id)
        profile = data.get("profile", {})
        
        try:
            # Get recommendations from AI engine
            result = self.pipeline.recommend(profile, include_educational=False)
            recommended = result.get('recommended_methods', [])
            
            if not recommended:
                session_manager.delete_session(session_id)
                return USSDResponse.end(
                    "No suitable methods found. Please consult a healthcare provider.\n\n"
                    "Thank you for using NuruCare!"
                )
            
            # Build results message (USSD character limit ~160 per screen)
            # Show top 3 methods
            response = "Your Top Recommendations:\n\n"
            
            for i, method in enumerate(recommended[:3], 1):
                confidence = method.get('confidence_score', 0)
                method_name = method.get('method_name', 'Unknown')
                response += f"{i}. {method_name}\n"
                response += f"   Confidence: {confidence:.0f}%\n\n"
            
            response += "Reply with method number for details,\n"
            response += "or 0 to exit"
            
            # Store results for detail view
            session_manager.update_session(session_id, {"recommendations": recommended})
            session_manager.set_step(session_id, 16)
            
            return USSDResponse.con(response)
            
        except Exception as e:
            session_manager.delete_session(session_id)
            return USSDResponse.end(
                "Error generating recommendations. Please try again later.\n\n"
                "Thank you for using NuruCare!"
            )
    
    # --- Step 16: Method Details ---
    async def _method_details(self, user_input: str, session_id: str) -> dict:
        data = session_manager.get_data(session_id)
        recommendations = data.get("recommendations", [])
        
        try:
            idx = int(user_input)
            if idx == 0:
                session_manager.delete_session(session_id)
                return USSDResponse.end(
                    "Thank you for using NuruCare!\n\n"
                    "For more information, visit our website."
                )
            
            if 1 <= idx <= len(recommendations):
                method = recommendations[idx - 1]
                response = f"Method Details:\n\n"
                response += f"{method.get('method_name', 'Method')}\n"
                response += f"Confidence: {method.get('confidence_score', 0):.0f}%\n"
                response += f"Explanation: {method.get('explanation', 'N/A')[:80]}...\n\n"
                response += "Reply 0 to exit"
                
                return USSDResponse.con(response)
        except:
            pass
        
        return USSDResponse.con("Invalid choice. Reply with a method number or 0 to exit.")


# ============================================
# API ENDPOINT
# ============================================

@router.post("/callback")
async def ussd_callback(request: USSDRequest):
    """
    Main USSD callback endpoint.
    
    Africa's Talking sends a POST request to this URL with:
    - sessionId: Unique per session
    - serviceCode: The USSD code dialed
    - phoneNumber: User's phone number
    - text: What the user typed (accumulated)
    """
    try:
        session_id = request.sessionId
        phone_number = request.phoneNumber
        text = request.text
        
        # Set phone number in session
        session_manager.set_phone_number(session_id, phone_number)
        
        # Determine the user's input (last segment)
        user_input = text.split('*')[-1] if text else ""
        
        # Get current step
        current_step = session_manager.get_step(session_id)
        
        # If user inputs 0 during the flow, end session
        if user_input == "0" and current_step > 0 and current_step < 14:
            session_manager.delete_session(session_id)
            return {
                "text": "Thank you for using NuruCare!\n\n"
                        "For more information, visit our website.",
                "type": "end"
            }
        
        # Handle the flow
        flow = USSDIntakeFlow()
        response = await flow.handle(session_id, user_input, current_step)
        
        # Clean up if session ends
        if response["type"] == "end":
            session_manager.delete_session(session_id)
        
        return response
        
    except Exception as e:
        # Log error
        print(f"USSD Error: {e}")
        session_manager.delete_session(session_id)
        return {
            "text": "An error occurred. Please try again later.",
            "type": "end"
        }


# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@router.get("/health")
async def ussd_health_check():
    """Health check for USSD endpoint"""
    return {
        "status": "ok",
        "service": "NuruCare USSD Complete",
        "active_sessions": session_manager.count_active_sessions()
    }