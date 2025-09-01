from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.routing import Mount
import os
import sys
import yaml
import asyncio
from pathlib import Path
from typing import Dict, Any

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.diagnosis_agent.agent import symptom_checker_tool
from agents.drug_info_agent.agent import drug_info_tool
from agents.literature_search_agent.agent import literature_search_tool
from agents.scheduling_agent.agent import patient_interaction_tool
# from workflow_engine import get_workflow_engine, execute_medical_workflow

# Load agent configurations
def load_agent_configs() -> Dict[str, Any]:
    """Load agent configurations from YAML file"""
    config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load agent configs: {e}")
        return {}

# Additional agent handlers for missing agent types
def handle_radiology_query(message: str) -> str:
    """Handle radiology and imaging related queries"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["x-ray", "xray", "radiograph"]):
        return """🖼️ **X-Ray Information**

**What X-rays can show:**
• Bone fractures and breaks
• Joint problems and arthritis
• Lung conditions (pneumonia, fluid)
• Heart size and shape
• Foreign objects in the body

**Preparation for X-rays:**
• Remove jewelry and metal objects
• Wear comfortable, loose clothing
• Inform technician if pregnant
• Follow positioning instructions

**Safety Notes:**
• Minimal radiation exposure
• Generally safe for most patients
• Pregnant women need special precautions

Would you like information about a specific type of X-ray or imaging procedure?"""

    elif any(word in message_lower for word in ["mri", "magnetic"]):
        return """🖼️ **MRI Information**

**What MRI can detect:**
• Soft tissue injuries
• Brain and spinal cord conditions
• Joint and muscle problems
• Internal organ abnormalities
• Blood vessel issues

**Before your MRI:**
• Remove all metal objects
• Inform staff of any implants
• Wear MRI-safe clothing
• Arrive 30 minutes early

**Duration:** 15-90 minutes depending on scan type

**Note:** Some patients may need contrast dye for enhanced imaging.

Do you have questions about a specific MRI scan or preparation?"""

    elif any(word in message_lower for word in ["ct", "cat", "computed"]):
        return """🖼️ **CT Scan Information**

**CT scans are excellent for:**
• Emergency trauma assessment
• Cancer detection and monitoring
• Internal bleeding detection
• Bone and joint detailed imaging
• Abdominal and chest conditions

**Preparation may include:**
• Fasting for certain scans
• Contrast dye (oral or IV)
• Removing metal objects
• Comfortable clothing

**Safety:** Uses X-ray technology, higher radiation than regular X-rays

Would you like details about contrast dye or a specific CT procedure?"""

    else:
        return f"""🖼️ **Radiology & Imaging Information**

I can help you understand various imaging procedures:

**Common Imaging Types:**
• **X-rays** - Bones, chest, joints
• **MRI** - Soft tissues, brain, spine
• **CT Scans** - Detailed cross-sections
• **Ultrasound** - Real-time imaging
• **Mammography** - Breast screening

**Your Query:** "{message}"

**General Guidance:**
• Always follow preparation instructions
• Inform staff of medical history
• Ask about contrast agents if needed
• Bring previous imaging for comparison

What specific imaging procedure would you like to know about?"""

def handle_treatment_query(message: str) -> str:
    """Handle treatment and therapy related queries"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["physical therapy", "physiotherapy", "pt"]):
        return """🧾 **Physical Therapy Information**

**What Physical Therapy Helps:**
• Post-surgery recovery
• Sports injury rehabilitation
• Chronic pain management
• Balance and mobility issues
• Strength building

**Common Treatments:**
• Therapeutic exercises
• Manual therapy techniques
• Heat/cold therapy
• Electrical stimulation
• Ultrasound therapy

**Treatment Duration:**
• Initial evaluation: 45-60 minutes
• Follow-up sessions: 30-45 minutes
• Typical course: 6-12 weeks

**Tips for Success:**
• Follow home exercise programs
• Communicate pain levels honestly
• Be consistent with appointments
• Ask questions about your progress

Would you like information about a specific condition or PT technique?"""

    elif any(word in message_lower for word in ["medication", "prescription", "treatment plan"]):
        return """🧾 **Treatment Planning Information**

**Comprehensive Care Approach:**
• Accurate diagnosis first
• Evidence-based treatment options
• Patient preferences consideration
• Risk-benefit analysis
• Regular monitoring and adjustments

**Treatment Categories:**
• **Medications** - Prescription and OTC
• **Procedures** - Minimally invasive options
• **Therapy** - Physical, occupational, speech
• **Lifestyle** - Diet, exercise, stress management
• **Alternative** - Complementary approaches

**Important Considerations:**
• Drug interactions and allergies
• Underlying health conditions
• Insurance coverage
• Treatment adherence
• Side effect monitoring

**Questions to Ask Your Doctor:**
• What are my treatment options?
• What are the risks and benefits?
• How long will treatment take?
• What should I expect?

Would you like more specific information about any treatment approach?"""

    else:
        return f"""🧾 **Treatment & Care Information**

**Your Query:** "{message}"

**I can provide information about:**
• Treatment options for various conditions
• Physical therapy and rehabilitation
• Medication management
• Recovery timelines
• Post-treatment care

**Personalized Care Principles:**
• Evidence-based treatments
• Patient-centered approach
• Shared decision making
• Continuous monitoring
• Holistic health consideration

**Next Steps:**
• Consult with your healthcare provider
• Discuss treatment preferences
• Understand risks and benefits
• Plan for follow-up care

What specific aspect of treatment would you like to explore?"""

def handle_enterprise_query(message: str) -> str:
    """Handle enterprise and administrative queries"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["hipaa", "privacy", "compliance"]):
        return """🏢 **Healthcare Compliance & Privacy**

**HIPAA Compliance Features:**
• End-to-end encryption
• Audit trails and logging
• Access controls and authentication
• Data backup and recovery
• Staff training requirements

**Privacy Protections:**
• Patient data anonymization
• Secure communication channels
• Limited access on need-to-know basis
• Regular security assessments
• Incident response procedures

**Compliance Standards:**
• HIPAA (Health Insurance Portability)
• HITECH (Health Information Technology)
• State privacy regulations
• International standards (GDPR when applicable)

**Enterprise Security:**
• Multi-factor authentication
• Role-based permissions
• Regular security updates
• Penetration testing
• 24/7 monitoring

Need help with specific compliance requirements?"""

    elif any(word in message_lower for word in ["integration", "api", "ehr", "emr"]):
        return """🏢 **System Integration Capabilities**

**EHR/EMR Integration:**
• HL7 FHIR compatibility
• Real-time data synchronization
• Seamless workflow integration
• Custom API endpoints
• Legacy system support

**Supported Systems:**
• Epic, Cerner, Allscripts
• Custom healthcare platforms
• Laboratory information systems
• Pharmacy management systems
• Billing and administrative tools

**Integration Benefits:**
• Reduced data entry
• Improved accuracy
• Enhanced patient care
• Streamlined workflows
• Better reporting capabilities

**Implementation Support:**
• Technical consultation
• Custom development
• Testing and validation
• Staff training
• Ongoing maintenance

What specific integration requirements do you have?"""

    else:
        return f"""🏢 **Enterprise Healthcare Solutions**

**Your Query:** "{message}"

**Enterprise Capabilities:**
• **Scalability** - Handle thousands of users
• **Security** - HIPAA-compliant infrastructure
• **Integration** - Connect with existing systems
• **Analytics** - Advanced reporting and insights
• **Support** - 24/7 technical assistance

**Key Features:**
• Multi-location deployment
• Role-based access control
• Custom workflows and protocols
• Real-time monitoring and alerts
• Comprehensive audit trails

**Implementation Services:**
• Needs assessment
• Custom configuration
• Staff training programs
• Go-live support
• Ongoing optimization

**Contact Enterprise Sales:**
For detailed implementation planning and pricing, please contact our enterprise team.

What specific enterprise needs can I help you understand?"""

# Initialize workflow engine
agent_configs = load_agent_configs()
# workflow_engine = get_workflow_engine(agent_configs)

mcp = FastMCP("Multi-Agent Medical Assistant MCP Server")

# Add tools
mcp.tool()(symptom_checker_tool)
mcp.tool()(drug_info_tool)
mcp.tool()(literature_search_tool)
mcp.tool()(patient_interaction_tool)

# Create main FastAPI app
app = FastAPI(title="Multi-Agent Medical Assistant")

# Mount MCP server at /mcp
app.mount("/mcp", mcp.streamable_http_app())

# Mount static files
static_path = Path(__file__).parent.parent.parent / "frontend"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Load the advanced web interface
def load_web_interface() -> str:
    """Load the advanced web interface HTML"""
    web_interface_path = static_path / "index.html"
    try:
        with open(web_interface_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not load web interface: {e}")
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Medical Assistant</title></head>
        <body><h1>Multi-Agent Medical Assistant</h1><p>Loading interface...</p></body>
        </html>
        """

# Add web interface routes
@app.get("/", response_class=HTMLResponse)
async def home():
    return load_web_interface()

# Enhanced tool endpoints for chat interface
@app.post("/tool/symptom_checker")
async def handle_symptom_checker_web(symptoms: str = Form(...)):
    try:
        result = symptom_checker_tool(symptoms)
        return {"success": True, "data": result, "agent": "symptom_checker"}
    except Exception as e:
        print(f"Symptom checker error: {e}")
        return {
            "success": False,
            "error": "I'm having trouble analyzing symptoms right now. Please consult a healthcare professional for accurate diagnosis.",
            "fallback": "In the meantime, I recommend monitoring your symptoms and seeking medical attention if they worsen."
        }

@app.post("/tool/drug_info")
async def handle_drug_info_web(drug_name: str = Form(...)):
    try:
        result = drug_info_tool(drug_name)
        return {"success": True, "data": result, "agent": "drug_info"}
    except Exception as e:
        print(f"Drug info error: {e}")
        return {
            "success": False,
            "error": "I'm unable to access drug information at the moment.",
            "fallback": "Please consult your pharmacist or doctor for medication details and always check for potential interactions."
        }

@app.post("/tool/literature_search")
async def handle_literature_search_web(query: str = Form(...)):
    try:
        result = literature_search_tool(query)
        return {"success": True, "data": result, "agent": "literature_search"}
    except Exception as e:
        print(f"Literature search error: {e}")
        return {
            "success": False,
            "error": "I'm having difficulty accessing medical literature right now.",
            "fallback": "I recommend checking reputable sources like PubMed, NIH, or consulting with healthcare professionals for the latest research."
        }

@app.post("/tool/patient_interaction")
async def handle_patient_interaction_web(action: str = Form(...), details: str = Form(...)):
    try:
        result = patient_interaction_tool(action, details)
        return {"success": True, "data": result, "agent": "patient_interaction"}
    except Exception as e:
        print(f"Patient interaction error: {e}")
        return {
            "success": False,
            "error": "I'm experiencing some technical difficulties with patient services.",
            "fallback": "Please try again in a moment, or contact your healthcare provider directly for assistance."
        }

# New chat endpoint for conversational interface
@app.post("/chat")
async def handle_chat(request: dict):
    try:
        message = request.get("message", "")
        agent = (request.get("agent", "general") or "general").lower()

        # Log incoming chat for debugging
        print(f"/chat request received - agent: {agent} message: {message}")

        # Emergency detection
        emergency_keywords = ["emergency", "heart attack", "stroke", "severe pain", "unconscious", "bleeding", "can't breathe", "911", "urgent", "critical"]
        if any(keyword in message.lower() for keyword in emergency_keywords) or agent == "emergency":
            resp = """🚨 **MEDICAL EMERGENCY DETECTED** 🚨

**IMMEDIATE ACTION REQUIRED:**
• Call emergency services (911) NOW
• Go to the nearest emergency room
• Do not delay medical attention

**If you cannot call:**
• Have someone call for you
• Use emergency text services if available
• Ask someone to drive you to ER immediately

**While waiting for help:**
• Stay calm and breathe normally
• Do not leave the person alone
• Follow any instructions from emergency operators

⚠️ **This is not a substitute for professional emergency care**"""
            print("Emergency detected in /chat")
            return {"success": True, "response": resp, "agent": "emergency", "emergency": True}

        # Enhanced agent routing
        try:
            if agent in ["diagnostic", "symptom_checker", "symptoms"]:
                result = symptom_checker_tool(message)
                chosen = "diagnostic"

            elif agent in ["pharmacy", "drugs", "drug_info"]:
                result = drug_info_tool(message)
                chosen = "pharmacy"

            elif agent in ["radiology", "imaging", "scan"]:
                result = handle_radiology_query(message)
                chosen = "radiology"

            elif agent in ["treatment", "therapy", "care_plan"]:
                result = handle_treatment_query(message)
                chosen = "treatment"

            elif agent in ["enterprise", "admin", "management"]:
                result = handle_enterprise_query(message)
                chosen = "enterprise"

            elif agent in ["research", "literature"]:
                result = literature_search_tool(message)
                chosen = "research"

            else:
                # Smart routing based on message content
                if any(word in message.lower() for word in ["medication", "drug", "prescription", "pill", "pharmacy", "dosage"]):
                    result = drug_info_tool(message)
                    chosen = "pharmacy"
                elif any(word in message.lower() for word in ["symptom", "pain", "ache", "fever", "cough", "diagnosis", "sick"]):
                    result = symptom_checker_tool(message)
                    chosen = "diagnostic"
                elif any(word in message.lower() for word in ["x-ray", "mri", "ct", "scan", "imaging", "radiology"]):
                    result = handle_radiology_query(message)
                    chosen = "radiology"
                elif any(word in message.lower() for word in ["treatment", "therapy", "care", "plan", "recover"]):
                    result = handle_treatment_query(message)
                    chosen = "treatment"
                elif any(word in message.lower() for word in ["research", "study", "literature", "evidence", "paper"]):
                    result = literature_search_tool(message)
                    chosen = "research"
                else:
                    result = patient_interaction_tool("general_query", message)
                    chosen = "general"

        except Exception as inner_e:
            print(f"Agent execution error for agent={agent}: {inner_e}")
            return {
                "success": False, 
                "response": f"I'm experiencing technical difficulties with the {agent} agent. Please try again in a moment or contact your healthcare provider for assistance.",
                "agent": agent
            }

        # Ensure the response is a string
        if not isinstance(result, str):
            try:
                result = str(result)
            except Exception:
                result = "I'm having trouble generating a response. Please try rephrasing your question."

        print(f"/chat routed to {chosen}, response length={len(result)}")
        return {"success": True, "response": result, "agent": chosen}

    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "success": False,
            "response": "I'm sorry, I'm experiencing technical difficulties. Please try again in a moment, or contact your healthcare provider for immediate assistance.",
            "fallback": "For urgent medical concerns, please seek immediate medical attention."
        }

# Workflow management endpoints
@app.post("/workflow/execute")
async def execute_workflow(request: Request):
    """Execute a medical workflow"""
    try:
        data = await request.json()
        workflow_name = data.get("workflow_name")
        parameters = data.get("parameters", {})

        if not workflow_name:
            raise HTTPException(status_code=400, detail="workflow_name is required")

        # result = await execute_medical_workflow(workflow_name, parameters)
        return {"success": False, "error": "Workflow execution not implemented"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/workflow/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get the status of a workflow execution"""
    try:
        # status = workflow_engine.get_execution_status(workflow_id)
        # if status:
        #     return {"success": True, "data": status}
        # else:
        #     raise HTTPException(status_code=404, detail="Workflow not found")
        return {"success": False, "error": "Workflow engine not implemented"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/workflow/list")
async def list_workflows():
    """List all active workflow executions"""
    try:
        # workflows = workflow_engine.list_active_executions()
        return {"success": True, "data": []}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/workflow/cancel/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """Cancel a running workflow"""
    try:
        # cancelled = workflow_engine.cancel_execution(workflow_id)
        return {"success": False, "message": "Workflow engine not implemented"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents": list(agent_configs.keys()) if agent_configs else [],
        "workflows": ["emergency_triage", "routine_checkup"]  # Available workflow names
    }

# Analytics endpoint
@app.get("/analytics")
async def get_analytics():
    """Get system analytics"""
    try:
        # active_executions = len(workflow_engine.list_active_executions())
        return {
            "success": True,
            "data": {
                "active_workflows": 0,
                "total_agents": len(agent_configs) if agent_configs else 0,
                "system_status": "operational"
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Legacy HTML endpoints for backward compatibility
@app.post("/tool/symptom_checker", response_class=HTMLResponse)
async def handle_symptom_checker_legacy(symptoms: str = Form(...)):
    result = symptom_checker_tool(symptoms)
    return f"""
    <div class="container">
        <h1>Symptom Checker Result</h1>
        <div class="result">{result}</div>
        <br><a href="/">← Back to Home</a>
    </div>
    """

@app.post("/tool/drug_info", response_class=HTMLResponse)
async def handle_drug_info_legacy(drug_name: str = Form(...)):
    result = drug_info_tool(drug_name)
    return f"""
    <div class="container">
        <h1>Drug Information Result</h1>
        <div class="result">{result}</div>
        <br><a href="/">← Back to Home</a>
    </div>
    """

@app.post("/tool/literature_search", response_class=HTMLResponse)
async def handle_literature_search_legacy(query: str = Form(...)):
    result = literature_search_tool(query)
    return f"""
    <div class="container">
        <h1>Literature Search Result</h1>
        <div class="result">{result}</div>
        <br><a href="/">← Back to Home</a>
    </div>
    """

@app.post("/tool/patient_interaction", response_class=HTMLResponse)
async def handle_patient_interaction_legacy(action: str = Form(...), details: str = Form(...)):
    result = patient_interaction_tool(action, details)
    return f"""
    <div class="container">
        <h1>Patient Interaction Result</h1>
        <div class="result">{result}</div>
        <br><a href="/">← Back to Home</a>
    </div>
    """

if __name__ == "__main__":
    import uvicorn
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")  # Default to web server
    if transport == "streamable-http":
        print("Starting Multi-Agent Medical Assistant MCP Server on http://localhost:8000")
        print("Open your browser to http://localhost:8000 to access the chat interface")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        mcp.run(transport=transport)
