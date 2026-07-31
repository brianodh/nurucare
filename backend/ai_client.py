"""
NuruCare - AI Client (Mock Mode - No API Keys Required)
This version works without Gemini API. Add real keys later.
"""

def get_ai_recommendation(user_data: dict, narrative_summary: str = "", disclaimer: str = "") -> str:
    """
    Build a personalized narrative around the REAL recommendation pipeline's
    output. This does NOT independently decide which methods are safe — that
    would risk contradicting the actual WHO MEC guardrail/pipeline result
    (e.g. narrating a method as fine when the real engine restricted it for
    this exact profile). `narrative_summary` and `disclaimer` are the real,
    already-computed results from main.py's /api/v1/recommend endpoint
    (engine.recommendation_pipeline / engine.guardrail) — this function only
    formats them into a readable mock "AI" narrative. In MOCK MODE (no
    Gemini key configured) this is template text; the shape/contract stays
    identical so wiring in a real Gemini call later is a drop-in swap.
    """
    age = user_data.get('age', 25)
    parity = user_data.get('parity', 0)
    fertility = user_data.get('fertility_intention', 'long_term')
    smoking = user_data.get('smoking', False)
    breastfeeding = user_data.get('breastfeeding', False)
    migraine = user_data.get('migraine_type', 'none')

    recommended_section = narrative_summary.strip() if narrative_summary and narrative_summary.strip() else (
        "No specific methods could be ranked for this profile automatically — "
        "please consult a healthcare provider for personalized guidance."
    )
    reminders = disclaimer.strip() if disclaimer and disclaimer.strip() else (
        "Always consult a healthcare provider before starting any contraceptive method."
    )

    response = f"""
╔══════════════════════════════════════════════════════════════╗
║                    NURUCARE - YOUR RESULTS                    ║
╚══════════════════════════════════════════════════════════════╝

📊 YOUR PROFILE:
• Age: {age} years
• Children: {parity}
• Fertility goal: {fertility}
• Smoker: {smoking}
• Breastfeeding: {breastfeeding}
• Migraines: {migraine}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ RECOMMENDED METHODS FOR YOU:

{recommended_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 IMPORTANT REMINDERS:
• {reminders}
• Regular check-ups are recommended
• No method is 100% effective except abstinence
• You can change methods if you experience side effects

📞 Need more help? Visit your nearest health facility.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return response

def translate_to_swahili(text: str) -> str:
    """
    Translate English to Swahili - mock version
    """
    # Common translations
    translations = {
        "PROFILE": "TAARIFA ZAKO",
        "YOUR RESULTS": "MATOKEO YAKO",
        "RECOMMENDED METHODS FOR YOU": "NJIA ZINAZOPENDWA KWA AJILI YAKO",
        "METHODS NOT RECOMMENDED FOR YOU": "NJIA ZISIZOPENDWA KWA AJILI YAKO",
        "Age": "Umri",
        "Children": "Watoto",
        "Fertility goal": "Lengo la uzazi",
        "Smoker": "Mvutaji sigara",
        "Breastfeeding": "Kunyonyesha",
        "Migraines": "Kichwa kali",
        "Effectiveness": "Ufanisi",
        "Why it's good for you": "Kwa nini inafaa kwako",
        "Side effects": "Madhara",
        "Myth vs Fact": "Uongo vs Ukweli",
        "IMPORTANT REMINDERS": "VIKUMBUKO MUHIMU",
        "Always consult a healthcare provider": "Daima shauriana na mtoa huduma ya afya"
    }
    
    result = text
    for eng, swa in translations.items():
        result = result.replace(eng, swa)
    
    return result

def get_myth_busting(method_name: str) -> str:
    """
    Get myth vs fact for a specific method
    """
    myths = {
        "pill": "Myth: Pills cause infertility.\nFact: Fertility returns immediately after stopping.",
        "iud": "Myth: IUDs can get lost inside you.\nFact: IUDs are safely placed by a provider.",
        "condom": "Myth: Condoms are not effective.\nFact: When used correctly, condoms are 98% effective.",
        "implant": "Myth: Implants will make you infertile.\nFact: Implants are fully reversible.",
        "injectable": "Myth: Injectables cause permanent infertility.\nFact: Fertility returns, may take 6-12 months."
    }
    
    for key, myth in myths.items():
        if key in method_name.lower():
            return myth
    
    return f"Myth: {method_name} causes infertility.\nFact: {method_name} does not affect future fertility."

print("[OK] AI Client running in MOCK MODE (no API keys needed)")