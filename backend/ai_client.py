"""
NuruCare - AI Client (Mock Mode - No API Keys Required)
This version works without Gemini API. Add real keys later.
"""

def get_ai_recommendation(user_data: dict) -> str:
    """
    Get personalized contraceptive recommendation - mock version
    """
    age = user_data.get('age', 25)
    parity = user_data.get('parity', 0)
    fertility = user_data.get('fertility_intention', 'long_term')
    smoking = user_data.get('smoking', False)
    breastfeeding = user_data.get('breastfeeding', False)
    migraine = user_data.get('migraine_type', 'none')
    
    # Build response based on user data
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

"""
    
    # Age-based recommendations
    if age < 20:
        response += """
1️⃣ MALE CONDOMS
   • Effectiveness: 85% with typical use
   • Why it's good for you: No hormones, protects against STIs
   • Side effects: None
   • Myth vs Fact: "Condoms reduce pleasure" → False, modern condoms are thin

2️⃣ PROGESTIN-ONLY PILL (POP)
   • Effectiveness: 93% with perfect use
   • Why it's good for you: Safe for young women
   • Side effects: Irregular bleeding, headaches
   • Myth vs Fact: "Pills cause infertility" → False, fertility returns immediately

"""
    elif age < 35:
        response += """
1️⃣ PROGESTIN-ONLY PILL (POP)
   • Effectiveness: 93% with perfect use
   • Why it's good for you: Highly effective, reversible
   • Side effects: Irregular bleeding, breast tenderness
   • Myth vs Fact: "Hormonal methods make you gain weight" → Limited evidence

2️⃣ COPPER IUD
   • Effectiveness: 99% - one of the most effective
   • Why it's good for you: Long-acting (5-10 years), no hormones
   • Side effects: Heavier periods, more cramping
   • Myth vs Fact: "IUDs cause infertility" → False, fertility returns immediately

"""
    else:
        response += """
1️⃣ PROGESTIN-ONLY PILL (POP)
   • Effectiveness: 93% with perfect use
   • Why it's good for you: Safe for women over 35
   • Side effects: Irregular bleeding, headaches
   • Myth vs Fact: "Pills are dangerous after 35" → Only combined pills with smoking

2️⃣ COPPER IUD
   • Effectiveness: 99% - one of the most effective
   • Why it's good for you: No hormones, works for years
   • Side effects: Heavier periods, cramping
   • Myth vs Fact: "IUDs are painful" → Mild discomfort at insertion only

"""
    
    # Add condoms as third option for everyone
    response += """
3️⃣ MALE CONDOMS
   • Effectiveness: 85% with typical use
   • Why it's good for you: Protects against STIs, no side effects
   • Side effects: None
   • Myth vs Fact: "Condoms are not effective" → When used correctly, very effective

"""
    
    # Add restrictions if needed
    if smoking and age > 35:
        response += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ METHODS NOT RECOMMENDED FOR YOU:

⚠️ COMBINED ORAL CONTRACEPTIVES
   • Reason: Age > 35 + smoking increases cardiovascular risk
   • WHO Category: 4 (Unacceptable health risk)

"""
    
    if migraine == "with_aura":
        response += """
⚠️ COMBINED ORAL CONTRACEPTIVES
   • Reason: Migraine with aura increases stroke risk
   • WHO Category: 4 (Unacceptable health risk)

"""
    
    response += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 IMPORTANT REMINDERS:
• Always consult a healthcare provider before starting any method
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