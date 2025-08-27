# Personal Learning Projects Repository

This repository contains my personal learning projects developed during my Master's degree in Data Science at Pace University.

## Overview

- Each subfolder represents a different project or experiment completed as part of coursework, self-study, or exploration in data science, machine learning, and AI.
- Projects may include code, documentation, and sample data.

## 📁 Project Structure

```text
Projects/
├── AgenTech Research Hub/                          # Multi-agent AI research system
├── Personal-Document-Assistant-MCP/               # MCP server with RAG capabilities  
├── AI Data Analytics Agent/                       # Streamlit + Ollama analytics tool
├── Microsoft Stock Price Prediction Workflow (n8n)/ # n8n trading automation workflow
└── README.md                                      # This file
```

## Notable Projects

- **AgenTech Research Hub**: Advanced multi-agent AI research system with dynamic topic detection, real-time source gathering, and comprehensive REST API integration using CrewAI, LangGraph, and AutoGen frameworks.
- **Personal Document Assistant MCP Server**: A powerful Model Context Protocol server with RAG capabilities for VS Code integration, featuring local LLM processing and intelligent document management.
- **AI Data Analytics Agent**: An AI-powered analytics tool using Streamlit and Ollama for local LLM-based data analysis with support for CSV, Excel, and JSON data processing.
- **Microsoft Stock Price Prediction Workflow**: An automated n8n workflow for generating algorithmic trading signals (BUY/SELL/HOLD) for Microsoft stock using simulated LSTM/GRU predictions with Discord notifications.

---

## AgenTech Research Hub

An advanced multi-agent AI research system that leverages multiple AI frameworks for comprehensive research automation. The system provides intelligent topic detection, authoritative source gathering, and seamless integration across different operating modes.

### 🚀 Features

- **Multi-Agent Architecture**: Integrates CrewAI, LangGraph, and AutoGen frameworks
- **Dynamic Topic Detection**: Intelligent categorization across 15+ research domains
- **Authoritative Sources**: Real working URLs to trusted sources (WHO, NASA, IEEE, etc.)
- **Three Operating Modes**: Demo, Interactive, and REST API
- **Real-time Research**: Automated research with quality scoring and relevance ranking
- **Production Ready**: Comprehensive logging, error handling, and monitoring

### 🛠️ Installation

```bash
cd "AgenTech Research Hub"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/main.py
```

### 🎮 Operating Modes

**Demo Mode**: Automated research across 7 predefined topics

```bash
echo "1" | python3 src/main.py
```

**Interactive Mode**: Custom research queries with dynamic topic detection

```bash
echo "2" | python3 src/main.py
```

**API Mode**: REST API server for programmatic access

```bash
echo "3" | python3 src/main.py
# OR standalone API server
python3 api_server.py
```

### 📋 API Endpoints

- `GET /health` - Health check
- `GET /status` - System status
- `POST /research` - Perform research query

### 🔧 Supported Research Categories

Technology, Health, Environment, Finance, Education, Science, Food, Travel, Sports, Entertainment, Business, History, Politics, Arts, and General topics with specialized authoritative source mapping.

---

## Personal Document Assistant MCP Server

A powerful Model Context Protocol (MCP) server that provides intelligent document management and RAG (Retrieval-Augmented Generation) capabilities for VS Code.

### ✨ Key Features

- **Document Processing**: Upload and process PDF, DOCX, TXT, HTML documents
- **Semantic Search**: ChromaDB vector embeddings for intelligent document search
- **RAG Q&A**: Ask questions about your documents using local LLM
- **VS Code Integration**: Native integration through MCP protocol
- **Privacy-First**: All processing happens locally using Ollama

### ⚡ Setup Instructions

```bash
cd "Personal-Document-Assistant-MCP"
./setup.sh              # Install dependencies
ollama serve            # Start Ollama server
cd src && python demo.py   # Try the interactive demo
```

### 🎮 Interactive Demo

Experience all features with the built-in demo:

- Document processing with text chunking
- Live AI responses from local Ollama
- Storage system demonstration
- Complete workflow overview

### 📋 VS Code Integration

1. Install MCP extension in VS Code
2. Add server configuration to settings.json
3. Start uploading documents and asking questions!

**Available Tools**: upload_document, query_documents, search_documents, list_documents, get_document_info, delete_document, get_system_stats

---

## AI Data Analytics Agent (Ollama + Streamlit)

An intelligent data analytics tool that combines the power of local Large Language Models (LLMs) via Ollama with an intuitive Streamlit web interface. This application empowers users to perform comprehensive data analysis without relying on cloud-based AI services, ensuring privacy and data security.

### 🎯 Core Features

- **Multi-Format Data Support**: Upload and analyze CSV, Excel, or JSON datasets
- **Comprehensive Analytics Suite**:
  - Descriptive analytics for data exploration
  - Predictive modeling capabilities
  - Data cleaning and preprocessing tools
  - Interactive data visualization
- **Local LLM Integration**: Powered by Ollama models (Llama3, Mistral, etc.)
- **Privacy-First**: All processing happens locally on your machine
- **Interactive Interface**: User-friendly Streamlit dashboard

### 🚀 Quick Start

```bash
cd "AI Data Analytics Agent"
pip install -r requirements.txt
ollama serve  # Start Ollama server
ollama pull llama3  # Download model
streamlit run "Final Ai Agent.py"
```

### 📊 Analytics Capabilities

- **Data Profiling**: Automatic data type detection, missing value analysis, statistical summaries
- **Visualization**: Generate charts, plots, and graphs based on your data patterns
- **AI-Powered Insights**: Natural language explanations of data trends and patterns
- **Export Results**: Save analysis results and visualizations

---

## Microsoft Stock Price Prediction Workflow (n8n)

A sophisticated automated trading workflow built with n8n that combines financial data fetching, machine learning predictions, and real-time notifications for Microsoft (MSFT) stock trading signals.

### 🔄 Workflow Architecture

- **Daily Automation**: Scheduled execution with customizable timing
- **Data Pipeline**: Fetches MSFT historical prices from Yahoo Finance API
- **AI Predictions**: Simulates LSTM/GRU neural network models for price forecasting
- **Signal Generation**: Intelligent trading recommendations (BUY/SELL/HOLD)
- **Notification System**: Real-time alerts sent to Discord channels
- **Visual Workflow**: Complete n8n automation with error handling

### ⚙️ Technical Components

- **Data Source**: Yahoo Finance API for real-time stock data
- **ML Models**: LSTM/GRU neural networks for time series prediction
- **Automation Platform**: n8n workflow orchestration
- **Communication**: Discord webhook integration
- **Scheduling**: Configurable execution timing

### 🎯 Use Cases

- **Algorithmic Trading**: Automated signal generation for trading decisions
- **Market Analysis**: Daily stock price movement predictions
- **Portfolio Management**: Risk assessment and position sizing recommendations
- **Educational**: Learn about automated trading systems and ML in finance

---

## Other Projects

### Trading LSTM - Microsoft n8n

An automated trading workflow that combines LSTM neural networks with n8n automation for Microsoft stock predictions.

**Features:**

- Automated daily execution with customizable scheduling
- Fetches MSFT historical prices from Yahoo Finance API
- Simulates LSTM/GRU model predictions for price movement
- Generates intelligent trading signals (BUY/SELL/HOLD)
- Sends formatted notifications to Discord channels
- Complete workflow automation using n8n platform

**Technologies:** Python, LSTM/GRU Neural Networks, n8n, Yahoo Finance API, Discord Integration

## 🔧 Technologies Used

- **Languages**: Python, HTML, CSS, JavaScript
- **ML/AI**: scikit-learn, TensorFlow, LSTM/GRU Networks, Ollama, ChromaDB
- **AI Frameworks**: CrewAI, LangGraph, AutoGen
- **Web Frameworks**: Streamlit, FastAPI, uvicorn
- **Data Processing**: pandas, numpy, matplotlib, seaborn
- **Automation**: n8n workflow automation
- **APIs**: Yahoo Finance API, Discord API, REST APIs
- **Protocols**: Model Context Protocol (MCP)
- **Tools**: VS Code, Git, Docker

## 👨‍💻 Author & License

All code and content in this repository is for educational and personal use.

**Somesh Ramesh Ghaturle**  
MS in Data Science, Pace University

📧 **Email:** [someshghaturle@gmail.com](mailto:someshghaturle@gmail.com)  
🐙 **GitHub:** [https://github.com/somesh-ghaturle](https://github.com/somesh-ghaturle)  
💼 **LinkedIn:** [https://www.linkedin.com/in/someshghaturle/](https://www.linkedin.com/in/someshghaturle/)
