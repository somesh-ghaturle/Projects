import requests

def drug_info_tool(drug_name: str) -> str:
    """Comprehensive drug information with enhanced fallback for common medications."""
    drug_name_lower = drug_name.lower().strip()
    
    # Enhanced database of common medications with detailed information
    common_drugs = {
        "aspirin": {
            "brand_names": ["Bayer Aspirin", "Bufferin", "Ecotrin"],
            "generic": "Acetylsalicylic acid",
            "uses": "Pain relief, fever reduction, heart attack prevention, stroke prevention",
            "dosage": "Adults: 325-650mg every 4 hours for pain/fever. Low-dose (81mg) daily for heart protection",
            "warnings": "Do not give to children under 18 due to Reye's syndrome risk. Avoid if allergic to salicylates",
            "interactions": "Blood thinners, alcohol, certain diabetes medications"
        },
        "tylenol": {
            "brand_names": ["Tylenol", "Panadol", "Acetaminophen"],
            "generic": "Acetaminophen",
            "uses": "Pain relief, fever reduction",
            "dosage": "Adults: 325-1000mg every 4-6 hours, max 4000mg/day",
            "warnings": "Do not exceed recommended dose. Liver damage risk with alcohol or overdose",
            "interactions": "Alcohol, blood thinners like warfarin"
        },
        "ibuprofen": {
            "brand_names": ["Advil", "Motrin", "Nuprin"],
            "generic": "Ibuprofen",
            "uses": "Pain relief, fever reduction, inflammation reduction",
            "dosage": "Adults: 200-400mg every 4-6 hours, max 1200mg/day OTC",
            "warnings": "Take with food. Avoid if kidney problems, heart conditions, or stomach ulcers",
            "interactions": "Blood pressure medications, blood thinners, lithium"
        },
        "acetaminophen": {
            "brand_names": ["Tylenol", "Panadol"],
            "generic": "Acetaminophen",
            "uses": "Pain relief, fever reduction",
            "dosage": "Adults: 325-1000mg every 4-6 hours, max 4000mg/day",
            "warnings": "Do not exceed recommended dose. Liver damage risk with alcohol or overdose",
            "interactions": "Alcohol, blood thinners like warfarin"
        },
        "benadryl": {
            "brand_names": ["Benadryl", "Diphen"],
            "generic": "Diphenhydramine",
            "uses": "Allergies, hay fever, motion sickness, sleep aid",
            "dosage": "Adults: 25-50mg every 4-6 hours, max 300mg/day",
            "warnings": "Drowsiness, dry mouth. Avoid driving. Not for children under 2",
            "interactions": "Alcohol, sedatives, certain antidepressants"
        }
    }
    
    # Check for common drugs first
    for drug_key, info in common_drugs.items():
        if drug_key in drug_name_lower or any(brand.lower() in drug_name_lower for brand in info["brand_names"]):
            return f"""💊 **{info["brand_names"][0]} ({info["generic"]})**

📋 **What it's used for:**
{info["uses"]}

💉 **How to take it:**
{info["dosage"]}

⚠️ **Important Safety Information:**
{info["warnings"]}

🔄 **Drug Interactions:**
Avoid or use caution with: {info["interactions"]}

📞 **Important Notes:**
• Always follow package directions or doctor's instructions
• Tell your doctor about all medications you're taking
• Report any side effects to your healthcare provider
• Keep out of reach of children
• Store in a cool, dry place

**Common Brand Names:** {', '.join(info["brand_names"])}

Need more specific information? Ask your pharmacist or healthcare provider."""

    # Handle general queries about symptoms/conditions
    if any(word in drug_name_lower for word in ["fever", "temperature", "hot"]):
        return """💊 **Fever Management Options**

**Over-the-Counter Medications:**
• **Acetaminophen (Tylenol)** - Safe for most people, gentle on stomach
• **Ibuprofen (Advil, Motrin)** - Also reduces inflammation
• **Aspirin** - For adults only (not children under 18)

**Dosage Guidelines:**
• Acetaminophen: 325-1000mg every 4-6 hours (max 4000mg/day)
• Ibuprofen: 200-400mg every 4-6 hours with food
• Follow package instructions carefully

**Non-Medicine Options:**
• Rest and stay hydrated
• Cool compresses or lukewarm baths
• Light clothing and cool environment

**When to Seek Medical Care:**
• Fever >103°F (39.4°C)
• Fever lasting >3 days
• Difficulty breathing or severe symptoms
• Signs of dehydration

Always consult your healthcare provider for persistent or concerning symptoms."""

    elif any(word in drug_name_lower for word in ["pain", "ache", "headache"]):
        return """💊 **Pain Relief Options**

**Common OTC Pain Relievers:**
• **Acetaminophen (Tylenol)** - Good first choice, gentle on stomach
• **Ibuprofen (Advil, Motrin)** - Also reduces swelling/inflammation
• **Aspirin** - Effective but harder on stomach
• **Naproxen (Aleve)** - Longer-lasting relief

**Choosing the Right Option:**
• **For headaches:** Acetaminophen or ibuprofen
• **For muscle aches:** Ibuprofen or naproxen
• **For arthritis:** NSAIDs like ibuprofen work well
• **With stomach issues:** Acetaminophen preferred

**Safety Tips:**
• Don't exceed recommended doses
• Take NSAIDs with food
• Avoid mixing different pain relievers
• Check other medications for same ingredients

**See a Doctor If:**
• Pain is severe or worsening
• Pain persists beyond a few days
• Signs of medication side effects

Would you like specific information about any of these medications?"""

    elif any(word in drug_name_lower for word in ["allergy", "allergic", "hay fever", "sneezing"]):
        return """💊 **Allergy Medication Options**

**Antihistamines:**
• **Loratadine (Claritin)** - Non-drowsy, 24-hour relief
• **Cetirizine (Zyrtec)** - Fast-acting, may cause mild drowsiness
• **Fexofenadine (Allegra)** - Non-drowsy, good for severe allergies
• **Diphenhydramine (Benadryl)** - Causes drowsiness, short-acting

**Nasal Sprays:**
• **Fluticasone (Flonase)** - Steroid spray, takes days to work
• **Azelastine (Astelin)** - Fast-acting antihistamine spray

**For Specific Symptoms:**
• **Runny nose/sneezing:** Oral antihistamines
• **Stuffy nose:** Decongestants or nasal sprays
• **Itchy eyes:** Antihistamine eye drops

**Usage Tips:**
• Start treatment before allergy season
• Non-drowsy options for daytime use
• Don't use decongestant sprays >3 days
• Consider allergy shots for severe cases

Need help choosing based on your specific symptoms?"""

    # If no common drug match, try FDA API as fallback
    try:
        response = requests.get(f"https://api.fda.gov/drug/label.json?search=brand_name:{drug_name}&limit=1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and data['results']:
                result = data['results'][0]
                brand_name = result.get('brand_name', [drug_name])[0]
                generic_name = result.get('generic_name', ['Not specified'])[0]
                indications = result.get('indications_and_usage', ['No indications available'])[0]
                warnings = result.get('warnings', ['No warnings available'])[0]
                dosage = result.get('dosage_and_administration', ['Consult your doctor'])[0]
                interactions = result.get('drug_interactions', ['Not specified'])[0]

                return f"""💊 **{brand_name} ({generic_name})**

📋 **What it's used for:**
{indications[:400]}{'...' if len(indications) > 400 else ''}

⚠️ **Important Safety Information:**
{warnings[:400]}{'...' if len(warnings) > 400 else ''}

💉 **How to take it:**
{dosage[:300]}{'...' if len(dosage) > 300 else ''}

🔄 **Drug Interactions:**
{interactions[:300]}{'...' if len(interactions) > 300 else ''}

📞 **Important Notes:**
• Always take exactly as prescribed
• Tell your doctor about all medications you're taking
• Report any side effects to your healthcare provider
• Keep out of reach of children

Would you like me to check for specific interactions with another medication?"""
    
    except Exception:
        pass  # Continue to fallback response
    
    # Comprehensive fallback response
    return f"""🔍 **Drug Information Search: "{drug_name}"**

I don't have specific information about "{drug_name}" in my current database, but I can help you find reliable information.

**🏥 Trusted Resources:**
• **Drugs.com** - Comprehensive drug database
• **WebMD** - Drug information and interactions
• **MedlinePlus** - NIH drug information
• **Your Pharmacist** - Personalized advice

**💡 Search Tips:**
• Try the generic name instead of brand name
• Check spelling and common abbreviations
• Search for the condition it treats

**❓ Common Questions I Can Help With:**
• Pain relief options
• Fever management
• Allergy medications
• Drug interactions
• Side effects to watch for

**🚨 Important:**
• Always consult your healthcare provider for prescription medications
• Read all labels and follow directions
• Tell your doctor about all medications you take
• Keep medications in original containers

Would you like me to help with a specific medication category or symptom instead?"""
