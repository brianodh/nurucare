"""
NuruCare - USSD Handler for Africa's Talking
============================================

This module handles USSD interactions for offline accessibility.
Users dial *384*123# and complete the intake form via SMS-like menus.

Author: Brian Odhiambo Ouma
Date: July 2026
"""

import json
import re
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime

# Import your recommendation engine
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from engine.recommendation_pipeline import RecommendationPipeline

# Initialize router
router = APIRouter(prefix="/ussd", tags=["USSD"])

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
    text: str  # User's input (accumulated)


class USSDResponse(BaseModel):
    """USSD response format"""
    text: str
    type: str  # "con" for continue, "end" for end


# ============================================
# SESSION MANAGEMENT (In-Memory for Hackathon)
# ============================================

class USSDSessionManager:
    """
    Manages USSD sessions - stores user progress and data.
    
    For production, use Redis or a database. For the hackathon,
    in-memory storage is sufficient.
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict] = {}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or create a session"""
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "step": 0,
                "data": {},
                "created_at": datetime.now().isoformat()
            }
        return self._sessions[session_id]
    
    def update_session(self, session_id: str, data: Dict[str, Any]):
        """Update session data"""
        session = self.get_session(session_id)
        session["data"].update(data)
        self._sessions[session_id] = session
    
    def set_step(self, session_id: str, step: int):
        """Set current step"""
        session = self.get_session(session_id)
        session["step"] = step
        self._sessions[session_id] = session
    
    def get_step(self, session_id: str) -> int:
        """Get current step"""
        return self.get_session(session_id)["step"]
    
    def delete_session(self, session_id: str):
        """Delete session when complete"""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def get_data(self, session_id: str) -> Dict[str, Any]:
        """Get all collected data"""
        return self.get_session(session_id)["data"]


# Initialize session manager
session_manager = USSDSessionManager()


# ============================================
# USSD INTAKE FLOW HANDLER
# ============================================

class USSDFlow:
    """
    Complete USSD intake flow handler.
    
    Manages the step-by-step conversation with the user.
    """
    
    def __init__(self):
        self.pipeline = get_pipeline()
    
    def handle(self, session_id: str, user_input: str, current_step: int) -> USSDResponse:
        """
        Route to the appropriate step handler.
        
        Args:
            session_id: Unique session identifier
            user_input: User's latest input (single response)
            current_step: Current step number
            
        Returns:
            USSDResponse with the next menu or end message
        """
        
        # Route based on current step
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
            return self._irregular_periods(user_input, session_id)
        
        elif current_step == 11:
            return self._fertility_intent(user_input, session_id)
        
        elif current_step == 12:
            return self._breastfeeding(user_input, session_id)
        
        elif current_step == 13:
            return self._side_effects(user_input, session_id)
        
        elif current_step == 14:
            return self._processing(session_id)
        
        elif current_step == 15:
            return self._results(user_input, session_id)
        
        elif current_step == 16:
            return self._method_details(user_input, session_id)
        
        else:
            return USSDResponse(
                text="Session expired. Please dial *384*123# again.",
                type="end"
            )
    
    # --- Step 0: Welcome ---
    def _welcome(self) -> USSDResponse:
        return USSDResponse(
            text="CON Welcome to NuruCare - AI Contraceptive Support\n\n"
                 "1. Continue\n"
                 "2. Cancel\n\n"
                 "Reply with 1 to continue",
            type="con"
        )
    
    # --- Step 1: Terms and Conditions ---
    def _terms(self, user_input: str, session_id: str) -> USSDResponse:
        if user_input == "1":
            session_manager.set_step(session_id, 2)
            return USSDResponse(
                text="CON Terms & Conditions\n\n"
                     "By continuing, you agree to our Terms & Privacy Policy.\n"
                     "Your data is encrypted and never shared.\n\n"
                     "1. I agree\n"
                     "2. I do not agree\n\n"
                     "Reply with 1 to continue",
                type="con"
            )
        elif user_input == "2":
            return USSDResponse(
                text="END Thank you for using NuruCare. Goodbye.",
                type="end"
            )
        else:
            return USSDResponse(
                text="CON Please reply with 1 to continue or 2 to cancel.",
                type="con"
            )
    
    # --- Step 2: Age ---
    def _age(self, user_input: str, session_id: str) -> USSDResponse:
        try:
            age = int(user_input)
            if 15 <= age <= 49:
                session_manager.update_session(session_id, {"age": age})
                session_manager.set_step(session_id, 3)
                return USSDResponse(
                    text="CON Relationship Status\n\n"
                         "1. Single\n"
                         "2. In a relationship\n"
                         "3. Married\n"
                         "4. Prefer not to say\n\n"
                         "Reply with 1-4",
                    type="con"
                )
            return USSDResponse(
                text="CON Invalid age. Please enter age between 15-49.",
                type="con"
            )
        except ValueError:
            return USSDResponse(
                text="CON Please enter a valid number (e.g., 28).",
                type="con"
            )
    
    # --- Step 3: Relationship Status ---
    def _relationship(self, user_input: str, session_id: str) -> USSDResponse:
        mapping = {
            "1": "Single",
            "2": "In a relationship",
            "3": "Married",
            "4": "Prefer not to say"
        }
        if user_input in mapping:
            session_manager.update_session(session_id, {"relationship": mapping[user_input]})
            session_manager.set_step(session_id, 4)
            return USSDResponse(
                text="CON Enter Systolic Blood Pressure (top number):\n\n"
                     "e.g., 120\n\n"
                     "Reply with a number",
                type="con"
            )
        return USSDResponse(
            text="CON Please reply with 1-4.",
            type="con"
        )
    
    # --- Step 4: Systolic BP ---
    def _bp_systolic(self, user_input: str, session_id: str) -> USSDResponse:
        try:
            bp = int(user_input)
            if 60 <= bp <= 200:
                session_manager.update_session(session_id, {"systolic_bp": bp})
                session_manager.set_step(session_id, 5)
                return USSDResponse(
                    text="CON Enter Diastolic Blood Pressure (bottom number):\n\n"
                         "e.g., 80\n\n"
                         "Reply with a number",
                    type="con"
                )
            return USSDResponse(
                text="CON Invalid systolic BP. Enter 60-200.",
                type="con"
            )
        except ValueError:
            return USSDResponse(
                text="CON Please enter a valid number (e.g., 120).",
                type="con"
            )
    
    # --- Step 5: Diastolic BP ---
    def _bp_diastolic(self, user_input: str, session_id: str) -> USSDResponse:
        try:
            bp = int(user_input)
            if 40 <= bp <= 120:
                session_manager.update_session(session_id, {"diastolic_bp": bp})
                session_manager.set_step(session_id, 6)
                return USSDResponse(
                    text="CON Do you currently smoke?\n\n"
                         "1. Yes\n"
                         "2. No\n\n"
                         "Reply with 1 or 2",
                    type="con"
                )
            return USSDResponse(
                text="CON Invalid diastolic BP. Enter 40-120.",
                type="con"
            )
        except ValueError:
            return USSDResponse(
                text="CON Please enter a valid number (e.g., 80).",
                type="con"
            )
    
    # --- Step 6: Smoking Status ---
    def _smoking(self, user_input: str, session_id: str) -> USSDResponse:
        mapping = {"1": True, "2": False}
        if user_input in mapping:
            session_manager.update_session(session_id, {"smoking": mapping[user_input]})
            session_manager.set_step(session_id, 7)
            return USSDResponse(
                text="CON Do you have migraines?\n\n"
                     "1. No migraines\n"
                     "2. Migraine without aura\n"
                     "3. Migraine with aura\n\n"
                     "Reply with 1-3",
                type="con"
            )
        return USSDResponse(
            text="CON Please reply with 1 or 2.",
            type="con"
        )
    
    # --- Step 7: Migraine Type ---
    def _migraine(self, user_input: str, session_id: str) -> USSDResponse:
        mapping = {
            "1": "none",
            "2": "without_aura",
            "3": "with_aura"
        }
        if user_input in mapping:
            session_manager.update_session(session_id, {"migraine_type": mapping[user_input]})
            session_manager.set_step(session_id, 8)
            return USSDResponse(
                text="CON When was your last menstrual period?\n\n"
                     "Format: DDMMYYYY\n"
                     "e.g., 11072026\n\n"
                     "Reply with date",
                type="con"
            )
        return USSDResponse(
            text="CON Please reply with 1-3.",
            type="con"
        )
    
    # --- Step 8: Last Menstrual Period ---
    def _lmp(self, user_input: str, session_id: str) -> USSDResponse:
        if len(user_input) == 8 and user_input.isdigit():
            # Validate date format (basic check)
            day = int(user_input[:2])
            month = int(user_input[2:4])
            year = int(user_input[4:8])
            if 1 <= day <= 31 and 1 <= month <= 12 and 2000 <= year <= 2030:
                session_manager.update_session(session_id, {"lmp": user_input})
                session_manager.set_step(session_id, 9)
                return USSDResponse(
                    text="CON How many days is your typical cycle?\n\n"
                         "e.g., 28\n\n"
                         "Reply with a number",
                    type="con"
                )
        return USSDResponse(
            text="CON Invalid format. Use DDMMYYYY (e.g., 11072026).",
            type="con"
        )
    
    # --- Step 9: Cycle Length ---
    def _cycle_length(self, user_input: str, session_id: str) -> USSDResponse:
        try:
            days = int(user_input)
            if 20 <= days <= 45:
                session_manager.update_session(session_id, {"cycle_length": days})
                session_manager.set_step(session_id, 10)
                return USSDResponse(
                    text="CON Do you have irregular periods?\n\n"
                         "1. No\n"
                         "2. Yes, irregular\n"
                         "3. Suspected hormonal imbalance\n\n"
                         "Reply with 1-3",
                    type="con"
                )
            return USSDResponse(
                text="CON Enter 20-45 days.",
                type="con"
            )
        except ValueError:
            return USSDResponse(
                text="CON Please enter a number (e.g., 28).",
                type="con"
            )
    
    # --- Step 10: Irregular Periods ---
    def _irregular_periods(self, user_input: str, session_id: str) -> USSDResponse:
        mapping = {
            "1": "No",
            "2": "Yes, irregular",
            "3": "Suspected hormonal imbalance"
        }
        if user_input in mapping:
            session_manager.update_session(session_id, {"irregular_periods": mapping[user_input]})
            session_manager.set_step(session_id, 11)
            return USSDResponse(
                text="CON When do you want to have children?\n\n"
                     "1. Within 1 year\n"
                     "2. In 1-5 years\n"
                     "3. No more children (long-term)\n"
                     "4. Unsure\n\n"
                     "Reply with 1-4",
                type="con"
            )
        return USSDResponse(
            text="CON Please reply with 1-3.",
            type="con"
        )
    
    # --- Step 11: Fertility Intentions ---
    def _fertility_intent(self, user_input: str, session_id: str) -> USSDResponse:
        mapping = {
            "1": "want_soon",
            "2": "want_later",
            "3": "no_more",
            "4": "unsure"
        }
        if user_input in mapping:
            session_manager.update_session(session_id, {"fertility_intent": mapping[user_input]})
            session_manager.set_step(session_id, 12)
            return USSDResponse(
                text="CON Are you currently breastfeeding?\n\n"
                     "1. Yes\n"
                     "2. No\n\n"
                     "Reply with 1 or 2",
                type="con"
            )
        return USSDResponse(
            text="CON Please reply with 1-4.",
            type="con"
        )
    
    # --- Step 12: Breastfeeding ---
    def _breastfeeding(self, user_input: str, session_id: str) -> USSDResponse:
        mapping = {"1": True, "2": False}
        if user_input in mapping:
            session_manager.update_session(session_id, {"breastfeeding": mapping[user_input]})
            session_manager.set_step(session_id, 13)
            return USSDResponse(
                text="CON Select side effects you want to avoid:\n\n"
                     "1. Weight gain\n"
                     "2. Mood shifts\n"
                     "3. Acne\n"
                     "4. Irregular bleeding\n"
                     "5. Low libido\n"
                     "6. None\n\n"
                     "Reply with numbers separated by commas\n"
                     "e.g., 1,3,5",
                type="con"
            )
        return USSDResponse(
            text="CON Please reply with 1 or 2.",
            type="con"
        )
    
    # --- Step 13: Side Effects to Avoid ---
    def _side_effects(self, user_input: str, session_id: str) -> USSDResponse:
        side_effect_map = {
            "1": "weight_gain",
            "2": "mood_shifts",
            "3": "acne",
            "4": "irregular_bleeding",
            "5": "low_libido",
            "6": "none"
        }
        
        # Parse comma-separated values
        try:
            selected = []
            for item in user_input.split(','):
                item = item.strip()
                if item in side_effect_map:
                    selected.append(side_effect_map[item])
            
            if selected:
                session_manager.update_session(session_id, {"side_effect_concerns": selected})
                session_manager.set_step(session_id, 14)
                return USSDResponse(
                    text="CON Processing your information...\n\n"
                         "Please wait",
                    type="con"
                )
        except:
            pass
        
        return USSDResponse(
            text="CON Invalid input. Use numbers separated by commas.\n"
                 "e.g., 1,3,5",
            type="con"
        )
    
    # --- Step 14: Processing ---
    def _processing(self, session_id: str) -> USSDResponse:
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
            "postpartum_weeks": 100,  # Default
            "fertility_intent": data.get("fertility_intent", "unsure"),
            "cycle_regularity": "regular" if data.get("irregular_periods") == "No" else "irregular"
        }
        
        # Store profile in session for results
        session_manager.update_session(session_id, {"profile": profile})
        session_manager.set_step(session_id, 15)
        
        return USSDResponse(
            text="CON Analyzing your profile...\n\n"
                 "Your results are ready!",
            type="con"
        )
    
    # --- Step 15: Results ---
    def _results(self, user_input: str, session_id: str) -> USSDResponse:
        data = session_manager.get_data(session_id)
        profile = data.get("profile", {})
        
        # Get recommendations from AI engine
        try:
            result = self.pipeline.recommend(profile, include_educational=False)
            recommended = result.get('recommended_methods', [])
            
            if not recommended:
                return USSDResponse(
                    text="END No suitable methods found. Please consult a healthcare provider.\n\n"
                         "Thank you for using NuruCare!",
                    type="end"
                )
            
            # Build results message (USSD character limit ~160 per screen)
            # We'll show top 3 methods
            response = "CON Your Top Recommendations:\n\n"
            
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
            
            return USSDResponse(
                text=response,
                type="con"
            )
            
        except Exception as e:
            return USSDResponse(
                text=f"END Error generating recommendations. Please try again later.\n\n"
                     f"Thank you for using NuruCare!",
                type="end"
            )
    
    # --- Step 16: Method Details ---
    def _method_details(self, user_input: str, session_id: str) -> USSDResponse:
        data = session_manager.get_data(session_id)
        recommendations = data.get("recommendations", [])
        
        try:
            idx = int(user_input)
            if idx == 0:
                session_manager.delete_session(session_id)
                return USSDResponse(
                    text="END Thank you for using NuruCare!\n\n"
                         "For more information, visit our website.",
                    type="end"
                )
            
            if 1 <= idx <= len(recommendations):
                method = recommendations[idx - 1]
                response = f"CON {method.get('method_name', 'Method')} - Details\n\n"
                response += f"Confidence: {method.get('confidence_score', 0):.0f}%\n"
                response += f"Explanation: {method.get('explanation', 'N/A')[:80]}...\n\n"
                response += "Reply 0 to exit"
                
                return USSDResponse(
                    text=response,
                    type="con"
                )
        except:
            pass
        
        return USSDResponse(
            text="CON Invalid choice. Reply with a method number or 0 to exit.",
            type="con"
        )


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
        # Parse user input
        session_id = request.sessionId
        phone_number = request.phoneNumber
        text = request.text
        
        # Determine the user's input (last segment)
        user_input = text.split('*')[-1] if text else ""
        
        # Get or create session
        session = session_manager.get_session(session_id)
        current_step = session_manager.get_step(session_id)
        
        # If this is a new session, reset step to 0
        if not text and current_step == 0:
            pass  # Already at welcome
        
        # If session is in progress and user inputs 0, end session
        if user_input == "0" and current_step > 0:
            session_manager.delete_session(session_id)
            return {
                "text": "END Thank you for using NuruCare!\n\n"
                        "For more information, visit our website.",
                "type": "end"
            }
        
        # Handle the flow
        flow = USSDFlow()
        response = flow.handle(session_id, user_input, current_step)
        
        # Clean up if session ends
        if response.type == "end":
            session_manager.delete_session(session_id)
        
        # Return response in Africa's Talking format
        return {
            "text": response.text,
            "type": response.type
        }
        
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"USSD Error: {e}")
        return {
            "text": "END An error occurred. Please try again later.",
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
        "service": "NuruCare USSD",
        "active_sessions": len(session_manager._sessions)
    }