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

## 🏥 Quick Start

### Prerequisites
```bash
Python 3.8+
pip package manager
Modern web browser
Docker (for production deployment)
```

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/medassist-ai-mcp.git
cd medassist-ai-mcp
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start the MCP server**:
```bash
cd mcp-server/main
python server.py
```

4. **Open the medical interface**:
```bash
# Open frontend/index.html in your browser
# Or access: http://localhost:8000
```

## 🐳 Docker Production Deployment

### Production Setup
The application uses a robust multi-container architecture optimized for medical environments:

#### 1. FastAPI MCP Server Container
- **Base Image**: Python 3.11 slim
- **Health Checks**: Every 30 seconds for medical reliability
- **Auto-Restart**: On failure for continuous availability
- **HIPAA Compliance**: Secure container environment

#### 2. Nginx Reverse Proxy
- **Load Balancing**: Medical interface traffic distribution
- **Static Files**: Optimized serving of medical UI assets
- **Security**: Rate limiting and medical data protection headers
- **SSL/TLS**: Encryption for medical data transmission

### Quick Production Start

```bash
# Start production environment
docker-compose -f docker-compose.production.yml up -d

# Access the medical platform
open http://localhost:8080
```

### Container Management Commands

```bash
# View running medical containers
docker-compose -f docker-compose.production.yml ps

# View real-time medical system logs
docker-compose -f docker-compose.production.yml logs -f

# Stop the medical platform
docker-compose -f docker-compose.production.yml down

# Rebuild and restart (after medical system updates)
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# View medical container resource usage
docker stats
```

### Production Environment Variables
Create `.env.production` file:

```bash
# Medical API Configuration
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
MEDICAL_MODE=production

# External Medical APIs (Optional)
FDA_API_KEY=your_fda_api_key_here
MEDICAL_DB_ENABLED=true

# Security Settings for Medical Data
CORS_ORIGINS=["https://your-medical-domain.com"]
HIPAA_COMPLIANCE=true
SECURE_HEADERS=true

# Performance Tuning for Medical Workloads
CACHE_TTL=300
AGENT_TIMEOUT=60
MEDICAL_RESPONSE_CACHE=true
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
MedAssist Al MCP/
├── � README.md                          # Project documentation
├── 🖼️ medassist ai.png                   # Project preview image
├── 📋 requirements.txt                   # Python dependencies
├── 
├── 🤖 agents/                            # Medical AI Agents
│   ├── diagnostic_agent.py              # Diagnostic analysis
│   ├── pharmacy_agent.py                # Medication management
│   ├── radiology_agent.py               # Medical imaging
│   ├── treatment_agent.py               # Treatment planning
│   ├── emergency_agent.py               # Emergency response
│   └── enterprise_agent.py              # Healthcare management
├── 
├── �️ frontend/                          # Medical web interface
│   └── index.html                       # Professional dark theme UI
├── 
├── 🏥 mcp-server/                        # Model Context Protocol server
│   └── main/
│       └── server.py                    # FastAPI MCP server
├── 
├── � data/                              # Medical data storage
├── ✅ tests/                             # Unit and integration tests
└── �️ vector-db/                        # Medical knowledge database
```

## �‍💻 About the Developer

**Somesh Ghaturle**
- 🎓 **Education**: Master's in Computer Science, Pace University (Current Student)
- 💼 **Specialization**: AI/ML Engineering, Medical AI Systems, Multi-Agent Architectures
- � **Location**: New York, USA
- 🔬 **Research Focus**: Healthcare AI, Agent-Based Medical Systems, HIPAA-Compliant AI Solutions

### 📫 Contact Information

- **Email**: [someshghaturle@gmail.com](mailto:someshghaturle@gmail.com)
- **LinkedIn**: [Somesh Ghaturle](https://linkedin.com/in/someshghaturle)
- **GitHub**: [@someshghaturle](https://github.com/someshghaturle)
- **Portfolio**: [AI/ML Projects Collection](https://github.com/someshghaturle/ai-ml-portfolio)

### 🏆 Professional Background
- 🎯 Advanced expertise in Python, FastAPI, and AI/ML frameworks
- 🏥 Specialized in developing HIPAA-compliant medical AI systems
- 🤖 Expert in multi-agent architectures and intelligent system design
- 📊 Proven track record in healthcare technology and medical informatics

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern AI/ML technologies and medical industry best practices
- Designed for healthcare professionals and medical institutions
- Compliant with healthcare data protection standards (HIPAA)
- Powered by advanced multi-agent AI architecture

---

<div align="center">

**🏥 MedAssist AI MCP - Revolutionizing Healthcare with AI 🚀**

Made with ❤️ by [Somesh Ghaturle](https://github.com/someshghaturle)

[![Email](https://img.shields.io/badge/Email-someshghaturle@gmail.com-red)](mailto:someshghaturle@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/someshghaturle)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/someshghaturle)

</div>

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
