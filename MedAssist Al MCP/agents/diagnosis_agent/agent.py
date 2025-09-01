def symptom_checker_tool(symptoms: str) -> str:
    """Advanced symptom analysis and diagnostic support with evidence-based recommendations."""
    symptoms_lower = symptoms.lower()

    # Emergency symptom detection
    emergency_symptoms = ["chest pain", "difficulty breathing", "severe headache", "stroke", "heart attack", "unconscious", "severe bleeding"]
    if any(symptom in symptoms_lower for symptom in emergency_symptoms):
        return """🚨 **CRITICAL MEDICAL ALERT** 🚨

**IMMEDIATE ACTION REQUIRED:**
• Call 911 or go to nearest emergency room NOW
• Do not delay seeking medical attention
• Time is critical for your safety

**Emergency Symptoms Detected:**
Your symptoms may indicate a serious medical emergency that requires immediate professional medical care.

**While waiting for emergency services:**
• Stay calm and avoid strenuous activity
• Have someone stay with you if possible
• Follow any instructions from emergency operators
• Bring a list of current medications

⚠️ **This is not medical advice - seek immediate professional care**"""

    if "fever" in symptoms_lower and "cough" in symptoms_lower:
        return """🩺 **Symptom Analysis: Fever + Cough**

**Primary Differential Diagnoses:**
• **Viral Upper Respiratory Infection** (Most likely)
• **Influenza** (Seasonal consideration)
• **COVID-19** (Consider testing)
• **Bacterial Pneumonia** (If severe symptoms)

**Recommended Immediate Actions:**
1. **Monitor Temperature** - Track every 4-6 hours
2. **Hydration** - Increase fluid intake significantly
3. **Rest** - Avoid strenuous activities
4. **Isolation** - Prevent spread to others

**Symptom Management:**
• Acetaminophen or ibuprofen for fever
• Honey for cough (if over 1 year old)
• Warm salt water gargles
• Humidifier or steam inhalation

**Seek Medical Care If:**
• Fever >103°F (39.4°C) or persistent >3 days
• Difficulty breathing or chest pain
• Blood in cough or severe throat pain
• Symptoms worsen after initial improvement

**Follow-up Questions:**
• How long have you had these symptoms?
• Any recent travel or known exposures?
• Current medications or medical conditions?

Would you like specific medication recommendations or guidance on when to test for COVID-19?"""

    elif "headache" in symptoms_lower and "nausea" in symptoms_lower:
        return """🩺 **Symptom Analysis: Headache + Nausea**

**Possible Conditions to Consider:**
• **Migraine Headache** (Most common combination)
• **Tension Headache with GI upset**
• **Viral Gastroenteritis**
• **Medication Overuse Headache**
• **Dehydration**

**Immediate Relief Strategies:**
1. **Environment** - Dark, quiet room
2. **Hydration** - Small, frequent sips of clear fluids
3. **Cold Therapy** - Ice pack to forehead/neck
4. **Rest** - Lie down with head slightly elevated

**Warning Signs - Seek Immediate Care:**
• Sudden, severe "thunderclap" headache
• Headache with fever and neck stiffness
• Vision changes or confusion
• Headache after head injury

**Assessment Questions:**
• Pain scale 1-10 and location?
• First time experiencing this combination?
• Recent changes in sleep, diet, or stress?
• Any visual disturbances or light sensitivity?

**Treatment Options:**
• Over-the-counter pain relievers (follow package instructions)
• Anti-nausea medications if available
• Ginger tea for nausea relief

Would you like information about migraine triggers or preventive measures?"""

    elif "sore throat" in symptoms_lower:
        return """🩺 **Symptom Analysis: Sore Throat**

**Common Causes:**
• **Viral Pharyngitis** (80% of cases)
• **Strep Throat** (Bacterial - requires treatment)
• **Allergic Reactions**
• **Acid Reflux**
• **Dry Air Irritation**

**Self-Assessment - Strep Indicators:**
• Sudden onset severe throat pain
• High fever (>101°F)
• White patches on tonsils
• Swollen lymph nodes
• No cough present

**Home Treatment Options:**
• Warm salt water gargles (1/2 tsp salt in warm water)
• Throat lozenges or hard candy
• Warm liquids (tea with honey)
• Over-the-counter pain relievers

**See Healthcare Provider If:**
• Symptoms persist >48 hours without improvement
• High fever or difficulty swallowing
• White patches on throat or tonsils
• Severe pain preventing eating/drinking

**Prevention Tips:**
• Frequent hand washing
• Avoid sharing drinks/utensils
• Stay hydrated
• Use humidifier in dry environments

Would you like guidance on distinguishing viral vs. bacterial throat infections?"""

    elif "stomach" in symptoms_lower or "nausea" in symptoms_lower or "vomiting" in symptoms_lower:
        return """🩺 **Symptom Analysis: Gastrointestinal Issues**

**Possible Conditions:**
• **Viral Gastroenteritis** ("Stomach flu")
• **Food Poisoning**
• **Stress-Related Nausea**
• **Medication Side Effects**
• **Motion Sickness**

**Immediate Management:**
1. **BRAT Diet** - Bananas, Rice, Applesauce, Toast
2. **Clear Fluids** - Start with small sips every 15 minutes
3. **Rest** - Allow digestive system to recover
4. **Gradual Reintroduction** - Slowly add normal foods

**Hydration Solutions:**
• Oral rehydration solutions (Pedialyte)
• Clear broths or diluted sports drinks
• Ginger tea for nausea relief
• Avoid dairy and high-fat foods

**Seek Medical Care If:**
• Signs of severe dehydration (dizziness, dry mouth)
• Blood in vomit or stool
• High fever with abdominal pain
• Symptoms persist >48-72 hours

**Red Flags:**
• Severe abdominal pain
• Signs of appendicitis (right lower quadrant pain)
• Unable to keep fluids down for >24 hours

Would you like specific recommendations for rehydration or dietary management?"""

    else:
        return f"""🩺 **Comprehensive Symptom Assessment**

**Your Reported Symptoms:** "{symptoms}"

**To provide optimal diagnostic support, I need additional information:**

**Symptom Characterization:**
• **Duration** - How long have you experienced these symptoms?
• **Severity** - Rate from 1-10 (10 being severe)
• **Pattern** - Constant, intermittent, or worsening?
• **Location** - Specific body areas affected?

**Associated Symptoms:**
• Fever, chills, or night sweats?
• Changes in appetite or sleep?
• Any recent injuries or illnesses?
• Medications or supplements taken?

**Context Information:**
• Recent travel or exposure to illness?
• Stress levels or life changes?
• Family history of similar symptoms?
• Previous episodes of these symptoms?

**General Health Monitoring:**
• Track symptoms with time/date
• Note any triggering factors
• Monitor for improvement or worsening
• Stay hydrated and rest as needed

**When to Seek Care:**
• Symptoms persist or worsen
• Development of fever or severe pain
• Inability to perform daily activities
• Concerning changes in symptoms

Please provide more details about your symptoms, and I'll offer more specific guidance and recommendations."""



