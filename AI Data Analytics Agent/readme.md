# 📊 AI Data Analytics Agent

> **Intelligent data analytics platform powered by local LLMs and Streamlit for comprehensive data analysis workflows**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://github.com/somesh-ghaturle/Projects)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

**AI Data Analytics Agent** is a production-ready analytics platform that combines the power of local LLMs (via Ollama) with an intuitive Streamlit interface. The system provides comprehensive data analysis capabilities including descriptive analytics, predictive modeling, data cleaning, and custom AI-powered insights.

### ✨ Key Features

- **🤖 AI-Powered Analytics**: Local LLM integration via Ollama for intelligent data insights
- **📊 Comprehensive Analysis**: Descriptive, predictive, cleaning, and visualization capabilities
- **🌐 Professional Web Interface**: Clean Streamlit UI with tabbed organization
- **📁 Multi-Format Support**: CSV, Excel (XLSX), and JSON data processing
- **🐳 Production Ready**: Docker containerized with health monitoring
- **⚡ Timeout Protection**: Non-blocking LLM calls with worker thread implementation
- **🔒 Secure Uploads**: Configurable upload paths with read-only mount support

## 🏗️ System Architecture

```mermaid
flowchart TB
    subgraph "User Interface"
        UI[🌐 Streamlit Web Interface<br/>Port 8501]
        UPLOAD[📁 File Upload<br/>CSV/XLSX/JSON]
        TABS[📋 Analysis Tabs<br/>Descriptive | Predictive | Cleaning | Viz | Custom]
    end
    
    subgraph "Docker Environment" 
        subgraph "Application Container"
            APP[🚀 Analytics Core<br/>analytics_core.py]
            AGENT[🤖 Ollama Analytics Agent<br/>LLM Integration]
            WORKER[⚡ Worker Thread<br/>Timeout Protection]
        end
        
        subgraph "Data Processing"
            LOADER[📊 Data Loader<br/>Pandas + OpenPyXL]
            CACHE[💾 Data Cache<br/>In-Memory Storage]
            SAMPLER[🎯 Smart Sampling<br/>Large Dataset Handling]
        end
        
        subgraph "External Services"
            OLLAMA[🧠 Ollama LLM<br/>Local AI Processing]
            MODELS[🔧 Model Selection<br/>Auto llama3.2 preference]
        end
    end
    
    subgraph "File System"
        UPLOADS[📂 Upload Directory<br/>/tmp/app_uploads]
        DATA[📁 Data Mount<br/>/app/data (read-only)]
    end
    
    %% User Flow
    UPLOAD --> UI
    UI --> TABS
    TABS --> APP
    
    %% Processing Flow
    APP --> AGENT
    AGENT --> WORKER
    WORKER --> OLLAMA
    OLLAMA --> MODELS
    
    %% Data Flow
    UPLOAD --> UPLOADS
    APP --> LOADER
    LOADER --> CACHE
    CACHE --> SAMPLER
    SAMPLER --> AGENT
    
    %% External Data
    DATA --> LOADER
    
    style UI fill:#e1f5fe
    style AGENT fill:#f3e5f5
    style OLLAMA fill:#fff3e0
    style UPLOADS fill:#e8f5e8
```

## 🚀 Quick Start Guide

### Prerequisites

- Docker and Docker Compose installed
- Ollama running locally (default: `http://localhost:11434`)
- 4GB+ RAM recommended for optimal performance

### One-Command Production Deployment

```bash
# Navigate to project directory
cd "AI Data Analytics Agent"

# Build and start the production stack
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# Verify deployment
docker ps --filter name=ai-data-analytics -a
```

### Platform Access Points

- **🌐 Analytics Interface**: <http://localhost:8501>
- **📊 Health Check**: Container logs via `docker logs <container_id>`
- **🔧 Configuration**: Environment variables in `docker-compose.production.yml`

## 💻 Usage Examples

### Web Interface Workflow

1. **Access**: Navigate to <http://localhost:8501>
2. **Model Selection**: Choose Ollama model (auto-selects llama3.2 if available)
3. **Initialize**: Click "Initialize Agent" to connect to Ollama
4. **Upload Data**: Upload CSV, Excel, or JSON files
5. **Analysis**: Use tabs for different analysis types:
   - **Descriptive**: Statistical summaries and insights
   - **Predictive**: Forecasting and trend analysis
   - **Cleaning**: Data quality assessment and cleaning
   - **Visualizations**: Charts and plots generation
   - **Custom**: AI-powered custom analysis

### API Integration

While primarily a web interface, the core analytics can be imported:

```python
from analytics_core import OllamaAnalyticsAgent

# Initialize agent
agent = OllamaAnalyticsAgent()

# Load and analyze data
result = agent.load_and_analyze_data("data.csv")
print(f"Analysis: {result.analysis}")
```

## ⚙️ Configuration & Environment

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | Ollama server URL | `http://host.docker.internal:11434` |
| `OLLAMA_PREFERRED_MODEL` | Preferred model for auto-selection | `llama3.2` |
| `APP_UPLOAD_DIR` | Upload directory path | `/tmp/app_uploads` |

### File Structure

```text
AI Data Analytics Agent/
├── 🚀 web_ui.py                      # Streamlit web interface
├── 🤖 analytics_core.py              # Core analytics engine
├── 🐳 docker-compose.production.yml  # Production deployment
├── 📦 Dockerfile.production          # Production container build
├── 📋 requirements.txt               # Python dependencies
├── 🧪 tests/                         # Automated tests
│   ├── ui_playwright_smoke.py        # UI smoke test
│   └── ui_smoke_result.png           # Test screenshot
└── 📁 data/                          # Data directory (mounted read-only)
```

## 🛠️ Development Setup

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run web_ui.py
```

### Docker Development

```bash
# Build development image
docker-compose build

# Run with live reload
docker-compose up

# View logs
docker-compose logs -f
```

## 🧪 Testing & Verification

### Automated Testing

```bash
# Run UI smoke test (requires running server)
python tests/ui_playwright_smoke.py

# In-container health check
docker exec <container_id> python3 -c "
from analytics_core import OllamaAnalyticsAgent
agent = OllamaAnalyticsAgent()
print('✅ Agent initialized successfully')
print(f'Model: {agent.model_name}')
"
```

### Manual Testing Checklist

- [ ] Upload different file formats (CSV, XLSX, JSON)
- [ ] Test each analysis tab functionality
- [ ] Verify model selection and initialization
- [ ] Check timeout handling for large datasets
- [ ] Validate upload path configuration

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Ollama connection error** | Verify `OLLAMA_HOST` and ensure Ollama is running |
| **Read-only file system error** | Check upload path configuration, use `/tmp/app_uploads` |
| **Long-running analysis** | Implemented timeout protection, check model performance |
| **Port 8501 conflict** | Change port mapping in docker-compose or stop conflicting service |
| **Out of memory** | Use data sampling for large files, increase container memory |

### Advanced Configuration

#### Persistent Upload Storage

```yaml
# Add to docker-compose.production.yml
volumes:
  - ./data:/app/data:ro
  - ./uploads:/tmp/app_uploads  # Persistent uploads
```

#### Custom Model Configuration

```yaml
# Environment variables
environment:
  - OLLAMA_HOST=http://your-ollama-host:11434
  - OLLAMA_PREFERRED_MODEL=your-preferred-model
```

## 📊 Performance Metrics

- **Startup Time**: ~30 seconds (including model loading)
- **File Processing**: Up to 100MB files with automatic sampling
- **Analysis Speed**: 5-30 seconds depending on complexity and model
- **Memory Usage**: 2-4GB for typical operations
- **Concurrent Users**: Single-user design (Streamlit limitation)

## 🛡️ Security Considerations

- **Local Processing**: All data stays local, no external API calls
- **Read-only Mounts**: Data directory mounted read-only for protection
- **Isolated Uploads**: Uploads stored in dedicated container directory
- **No Data Persistence**: Analysis results not stored permanently

## 📈 Future Enhancements

- [ ] Multi-user support with session management
- [ ] Additional visualization types and customization
- [ ] Model performance benchmarking
- [ ] Integration with cloud storage providers
- [ ] Advanced caching mechanisms
- [ ] Real-time collaboration features

## 👨‍💻 Author & License

All code and content in this repository is for educational and personal use.

**Somesh Ramesh Ghaturle**  
MS in Data Science, Pace University

📧 **Email:** [someshghaturle@gmail.com](mailto:someshghaturle@gmail.com)  
🐙 **GitHub:** [https://github.com/somesh-ghaturle](https://github.com/somesh-ghaturle)  
💼 **LinkedIn:** [https://www.linkedin.com/in/someshghaturle/](https://www.linkedin.com/in/someshghaturle/)

### 📄 MIT License

```text
MIT License

Copyright (c) 2025 Somesh Ramesh Ghaturle

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

### Built with ❤️ using Streamlit, Ollama, and Python
