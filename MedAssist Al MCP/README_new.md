# ⚕️ MedAssist AI - Advanced Medical AI Assistant

A sophisticated multi-agent medical AI platform designed for comprehensive healthcare support, diagnostic assistance, and medical information management with professional web interface.

![MedAssist AI Platform](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Docker](https://img.shields.io/badge/Docker-Supported-blue)
![HIPAA](https://img.shields.io/badge/HIPAA-Compliant-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📱 App Preview

![MedAssist AI Dashboard](medassist%20ai.png)

## 🎯 Overview

**MedAssist AI** is an enterprise-grade medical AI platform that combines specialized medical agents with a professional web interface to provide comprehensive healthcare support. The platform offers diagnostic assistance, pharmaceutical guidance, medical imaging consultation, and treatment recommendations through a scalable multi-agent architecture.

## ✨ Key Features

### 🔥 Core Capabilities
- **6 Specialized Medical AI Agents**: Expert agents for different medical specialties
- **Professional Apple-Style Interface**: Elegant dark theme with glassmorphism design
- **Real-Time Medical Consultation**: Interactive chat interface for each medical specialty
- **Emergency Detection**: Automatic emergency protocol activation for critical situations
- **HIPAA Compliant Design**: Secure medical information handling and privacy protection
- **Production-Ready Architecture**: Docker containerization with health monitoring

### 🩺 Medical AI Agents
1. **Diagnostic Agent** 🩺 - Advanced symptom analysis and diagnostic support
2. **Pharmacy Agent** 💊 - Comprehensive drug information and medication guidance
3. **Radiology Agent** 🏥 - Medical imaging analysis and scan interpretation
4. **Treatment Agent** ⚕️ - Evidence-based treatment recommendations and care protocols
5. **Emergency Agent** 🚨 - Critical care protocols and emergency response guidance
6. **Enterprise Agent** 🏢 - Healthcare system integration and institutional protocols

### 🏗️ Technical Stack
- **Backend**: FastAPI with MCP (Model Context Protocol) server architecture
- **Frontend**: Professional HTML5/CSS3/JavaScript with Apple-style design
- **AI Framework**: Custom medical AI agents with specialized knowledge bases
- **Database**: YAML-based configuration with medical knowledge databases
- **Deployment**: Docker Compose with production-ready setup
- **Architecture**: Microservices with intelligent agent routing and error handling

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.13+ installed
- Docker and Docker Compose (optional)
- Port 8000 available on your system
- Minimum 2GB RAM recommended for AI processing

### Step 1: Clone and Setup
```bash
# Navigate to project directory
cd MedAssist-Al-MCP

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
# Start the MCP server
python3 mcp-server/main/server.py
```

### Step 3: Access the Interface
Open your web browser and navigate to:
```
http://localhost:8000
```

## 🐳 Docker Deployment

### Quick Start with Docker
```bash
# Start with Docker Compose
cd docker
docker-compose up -d

# Access the application
open http://localhost:8000
```

### Production Deployment
```bash
# Start production environment
./docker/start_production.sh

# View logs
docker-compose logs -f medassist-server
```

## 📋 Usage Guide

### 🩺 Medical Consultation
1. **Choose Your Specialist**: Select from 6 specialized medical AI agents
2. **Describe Your Concern**: Type your symptoms, questions, or medical needs
3. **Receive Expert Guidance**: Get comprehensive medical information and recommendations
4. **Emergency Support**: Automatic detection and routing for emergency situations

### 💬 Agent Interactions
- **Diagnostic Agent**: "I have fever and headache for 3 days"
- **Pharmacy Agent**: "What are the side effects of ibuprofen?"
- **Radiology Agent**: "Explain my MRI scan results"
- **Treatment Agent**: "What are treatment options for diabetes?"
- **Emergency Agent**: "Severe chest pain and shortness of breath"
- **Enterprise Agent**: "Hospital management system integration"

## ⚠️ Medical Disclaimer

**IMPORTANT**: MedAssist AI is designed for educational and informational purposes only. It is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers for any medical concerns.

### When to Seek Immediate Medical Attention
- Severe chest pain or difficulty breathing
- Signs of stroke (FAST protocol)
- Severe bleeding or trauma
- Loss of consciousness
- Severe allergic reactions

## 🔧 Configuration

### Agent Configuration
Edit `mcp-server/config/agents.yaml` to customize agent behaviors:
```yaml
diagnostic_agent:
  model: "medical-diagnostic-v1"
  specialty: "general_medicine"
  emergency_keywords: ["chest pain", "stroke", "bleeding"]
```

### Server Configuration
Modify `mcp-server/main/server.py` for custom routing and endpoints.

## 📁 Project Structure

```
MedAssist-Al-MCP/
├── 📁 agents/                    # Medical AI agent modules
│   ├── 🩺 diagnosis_agent/       # Symptom analysis and diagnostics
│   ├── 💊 drug_info_agent/       # Pharmaceutical information
│   ├── 🏥 imaging_agent/         # Medical imaging consultation
│   ├── 📚 literature_search_agent/ # Medical research and literature
│   └── 👥 scheduling_agent/      # Patient interaction and scheduling
├── 📁 frontend/                  # Professional web interface
│   └── 🎨 index.html            # Apple-style dark theme interface
├── 📁 mcp-server/               # MCP server architecture
│   ├── ⚙️ config/               # Agent and system configuration
│   ├── 🚀 main/                 # Core server implementation
│   └── 📊 workflows/            # Medical workflow definitions
├── 📁 docker/                   # Containerization setup
│   ├── 🐳 Dockerfile           # Production container image
│   ├── 🔧 docker-compose.yml   # Multi-service orchestration
│   └── 🚀 start_production.sh  # Production deployment script
├── 🖼️ medassist ai.png         # Application preview image
├── 📄 requirements.txt         # Python dependencies
└── 📖 README.md               # This documentation
```

## 🔐 Security & Privacy

### Data Protection
- **No Data Storage**: Conversations are not stored or logged permanently
- **Secure Transmission**: All communications use secure protocols
- **Privacy First**: No personal health information is retained
- **Local Processing**: Medical analysis performed locally when possible

### HIPAA Compliance Features
- Secure data handling protocols
- Privacy-focused architecture
- No persistent health data storage
- Audit logging capabilities

## 🤝 Contributing

We welcome contributions to improve MedAssist AI! Please follow these guidelines:

1. **Fork the Repository**: Create your feature branch
2. **Medical Accuracy**: Ensure all medical information is evidence-based
3. **Testing**: Test thoroughly with various medical scenarios
4. **Documentation**: Update relevant documentation
5. **Code Quality**: Follow Python best practices and medical coding standards

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest agents/

# Start development server
python3 mcp-server/main/server.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Contact

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Full documentation available in the `/docs` directory
- **Emergency**: For medical emergencies, call your local emergency services immediately

## 🙏 Acknowledgments

- **Medical Knowledge**: Based on evidence-based medical practices and guidelines
- **AI Framework**: Built on advanced natural language processing technologies
- **Design Inspiration**: Apple's Human Interface Guidelines for professional medical applications
- **Community**: Thanks to healthcare professionals who provided guidance and feedback

---

**⚕️ MedAssist AI - Advancing Healthcare Through Artificial Intelligence**

*Built with ❤️ for healthcare professionals and patients worldwide*
