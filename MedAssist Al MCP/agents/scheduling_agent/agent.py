def patient_interaction_tool(action: str, details: str = "") -> str:
    """Enhanced patient interaction with intelligent response routing."""
    action_lower = action.lower()
    details_lower = details.lower() if details else ""

    if action_lower == "schedule":
        return f"""📅 **Appointment Scheduling Assistant**

✅ **Request Received:** {details}

📋 **Appointment Types Available:**
• **Routine Check-up** - Annual physical, preventive care
• **Sick Visit** - Acute symptoms, urgent concerns  
• **Follow-up** - Post-treatment monitoring
• **Specialist Consultation** - Cardiology, endocrinology, etc.
• **Procedure/Testing** - Lab work, imaging, screenings

⏰ **Next Steps:**
1. You'll receive confirmation within 2 business hours
2. Arrive 15 minutes early for check-in
3. Bring insurance card, ID, and medication list
4. Prepare questions for your provider

📞 **Contact Information:**
• Call (555) 123-CARE for changes or questions
• Use patient portal for non-urgent requests
• Emergency? Call 911 or go to nearest ER

💡 **Appointment Preparation:**
• List all current symptoms with timing
• Note all medications, vitamins, supplements
• Bring previous test results or medical records
• Write down questions you want to ask

Need help preparing for a specific type of appointment?"""

    elif action_lower in ["qa", "general_query"]:
        # Enhanced intelligent routing based on query content
        if not details.strip():
            return """👋 **Welcome to MedAssist AI!**

I'm your comprehensive medical assistant. How can I help you today?

🔍 **I can assist with:**
• **🩺 Symptom Analysis** - Describe your symptoms for guidance
• **💊 Medication Questions** - Drug information and interactions
• **📚 Medical Research** - Latest evidence and treatment options
• **🖼️ Imaging Guidance** - X-ray, MRI, CT scan information
• **📅 Appointment Help** - Scheduling and preparation
• **🚑 Emergency Guidance** - Urgent care protocols

**Examples of what to ask:**
• "I have a headache and nausea"
• "Tell me about aspirin interactions"
• "What's the latest research on diabetes?"
• "When should I get an MRI?"
• "I need to schedule a check-up"

What would you like to know about?"""

        # Smart routing based on content
        if any(word in details_lower for word in ["medication", "drug", "pill", "prescription", "pharmacy"]):
            return f"""💊 **Medication Assistance**

**Your Question:** "{details}"

**Medication Guidance:**
I can help you understand medications, their uses, side effects, and interactions.

**Important Medication Safety:**
• Always take medications exactly as prescribed
• Don't stop medications without consulting your doctor
• Report side effects to your healthcare provider
• Keep an updated medication list
• Check for drug interactions before adding new medications

**Common Medication Questions:**
• "What is [medication name] used for?"
• "What are the side effects of [medication]?"
• "Can I take [drug A] with [drug B]?"
• "What should I do if I miss a dose?"

**For Specific Help:**
Ask me about a particular medication, and I'll provide detailed information about its uses, dosing, warnings, and interactions.

What specific medication question can I help you with?"""

        elif any(word in details_lower for word in ["pain", "headache", "fever", "cough", "sick", "symptom"]):
            return f"""🩺 **Symptom Assessment Support**

**Your Concern:** "{details}"

**Symptom Evaluation Approach:**
I can help analyze your symptoms and provide guidance on next steps.

**What I Need to Know:**
• **Duration** - How long have you had these symptoms?
• **Severity** - Rate your discomfort (1-10 scale)
• **Pattern** - Constant, intermittent, or worsening?
• **Associated symptoms** - Any other symptoms?
• **Triggers** - What makes it better or worse?

**When to Seek Immediate Care:**
🚨 Call 911 or go to ER for:
• Chest pain or difficulty breathing
• Severe headache with neck stiffness
• High fever with confusion
• Severe abdominal pain
• Loss of consciousness

**For Better Assessment:**
Please describe your symptoms in detail, including when they started, how severe they are, and any other associated symptoms.

What specific symptoms would you like me to help evaluate?"""

        elif any(word in details_lower for word in ["appointment", "schedule", "doctor", "visit"]):
            return f"""📅 **Appointment & Healthcare Navigation**

**Your Request:** "{details}"

**Appointment Types & When to Schedule:**
• **Urgent Care** - Same-day for acute but non-emergency issues
• **Primary Care** - Routine check-ups, ongoing health management
• **Specialist** - Referred care for specific conditions
• **Preventive Care** - Screenings, vaccines, wellness visits

**Before Your Appointment:**
• Prepare a list of symptoms and questions
• Gather medical history and current medications
• Check insurance coverage and referral requirements
• Plan to arrive 15 minutes early

**What to Bring:**
• Photo ID and insurance cards
• List of current medications
• Previous test results or medical records
• Payment method for copays

**Questions to Ask Your Doctor:**
• What is my diagnosis and treatment options?
• What are the risks and benefits?
• How long will treatment take?
• What should I watch for?

Need help preparing for a specific type of appointment or medical visit?"""

        else:
            return f"""🤔 **General Health Question**

**Your Question:** "{details}"

**Comprehensive Health Support:**
Thank you for your question! I'm here to provide evidence-based health information and guidance.

**Key Health Principles:**
• **Prevention** - Regular check-ups and healthy lifestyle
• **Early Detection** - Screening and monitoring for conditions
• **Evidence-Based Care** - Treatments proven by research
• **Patient-Centered** - Care tailored to your individual needs

**Areas I Can Help With:**
• Understanding medical conditions and treatments
• Medication information and safety
• Symptom evaluation and when to seek care
• Preventive health measures
• Healthcare navigation and preparation

**Important Reminder:**
While I provide reliable health information, I'm not a substitute for professional medical advice. Always consult with healthcare providers for:
• Diagnosis and treatment decisions
• Medication changes
• Serious or persistent symptoms
• Emergency medical situations

**Next Steps:**
1. Consider your specific health goals and concerns
2. Prepare questions for your healthcare provider
3. Schedule appropriate medical care if needed
4. Follow evidence-based health recommendations

What specific aspect of your health question would you like me to address?"""

    elif action_lower in ["reminder", "follow_up"]:
        return f"""🔔 **Health Monitoring & Follow-up**

📝 **Follow-up Topic:** {details}

**✅ Health Tracking Recommendations:**

**Daily Monitoring:**
• Track symptoms in a health journal
• Record medication timing and effects
• Note sleep patterns and energy levels
• Monitor mood and stress levels

**Weekly Assessment:**
• Review symptom patterns and trends
• Check medication adherence
• Evaluate lifestyle factor impacts
• Assess progress toward health goals

**Monthly Review:**
• Update medication and supplement lists
• Review health goals and achievements
• Plan upcoming medical appointments
• Assess need for specialist consultations

**📱 Digital Health Tools:**
• Smartphone apps for symptom tracking
• Wearable devices for activity monitoring
• Patient portals for test results
• Telehealth options for remote consultations

**🔄 Follow-up Schedule:**
• Schedule next appointment before leaving
• Set calendar reminders for medications
• Plan routine screenings and check-ups
• Update emergency contact information

**📞 When to Contact Your Provider:**
• New or worsening symptoms
• Medication side effects
• Questions about treatment plans
• Need for prescription refills

Would you like help setting up a specific health monitoring plan?"""

    else:
        return f"""❓ **How Can I Help You?**

I didn't quite understand what you'd like to do. Let me help you navigate our services!

🔧 **Available Services:**
• **🩺 Health Questions** - Ask about symptoms, conditions, treatments
• **💊 Medication Info** - Drug details, interactions, side effects
• **📅 Appointments** - Scheduling and preparation assistance
• **📚 Medical Research** - Latest evidence and clinical guidelines
• **🔔 Health Tracking** - Monitoring and follow-up support

**💬 How to Get Help:**
Just tell me what you need! For example:
• "I have chest pain" → Symptom evaluation
• "Tell me about blood pressure medication" → Drug information
• "I need to schedule a physical" → Appointment assistance
• "What's new in diabetes research?" → Literature search

**🚨 For Emergencies:**
Call 911 immediately for life-threatening situations. I can provide guidance, but emergency services are needed for immediate medical crises.

What would you like to know or do today?"""
