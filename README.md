# Personal Learning Projects Repository

This repository contains my personal learning projects developed during my Master's degree in Data Science at Pace University.

## Overview

- Each subfolder represents a different project or experiment completed as part of coursework, self-study, or exploration in data science, machine learning, and AI.
- Projects may include code, documentation, and sample data.

## 📁 Project Structure

```text
Projects/
├── Personal-Document-Assistant-MCP/    # MCP server with RAG capabilities
├── AI Data Analytics Agent/            # Streamlit + Ollama analytics tool
├── Trading LSTM - Microsoft n8n/       # LSTM trading model with n8n automation
└── README.md                           # This file
```

## Notable Projects

- **Personal Document Assistant MCP Server**: A powerful Model Context Protocol server with RAG capabilities for VS Code integration, featuring local LLM processing and intelligent document management.
- **AI Data Analytics Agent**: An AI-powered analytics tool using Streamlit and Ollama for local LLM-based data analysis.
- **Trading LSTM - Microsoft n8n**: LSTM neural network for trading predictions integrated with n8n workflow automation.

---

## Personal Document Assistant MCP Server

A powerful Model Context Protocol (MCP) server that provides intelligent document management and RAG (Retrieval-Augmented Generation) capabilities for VS Code.

### 🚀 Features

- **Document Processing**: Upload and process PDF, DOCX, TXT, HTML documents
- **Semantic Search**: ChromaDB vector embeddings for intelligent document search
- **RAG Q&A**: Ask questions about your documents using local LLM
- **VS Code Integration**: Native integration through MCP protocol
- **Privacy-First**: All processing happens locally using Ollama

### 🛠️ Quick Start

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

This app is an AI-powered data analytics tool using local LLMs via Ollama and a Streamlit web interface.

## Features

- Upload CSV, Excel, or JSON data
- Descriptive, predictive, cleaning, and visualization analytics
- Powered by local Ollama models (e.g., Llama3)

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/download) installed and running locally
- Git

## Installation & Usage

1. **Clone the repository:**

   ```sh
   git clone https://github.com/somesh-ghaturle/Projects.git
   cd Projects
   ```

2. **(Optional) Create a virtual environment:**

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Start Ollama:**

   ```sh
   ollama serve
   ollama pull llama3  # or your preferred model
   ```

5. **Run the Streamlit app:**

   ```sh
   streamlit run "AI Data Analytics Agent/Final Ai Agent.py"
   ```

6. **Open your browser:**
   - Go to [http://localhost:8501](http://localhost:8501)

## Notes

- Ollama must be running locally for the app to work.
- You can change the model in the app UI if you have multiple models installed.
- For best results, use a machine with sufficient RAM and CPU.

## Troubleshooting

- **Ollama connection error:** Make sure `ollama serve` is running and the model is pulled.
- **Port conflicts:** Ensure nothing else is using port 11434 (Ollama) or 8501 (Streamlit).
- **File upload issues:** Only CSV, Excel, or JSON files are supported.

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
- **Web Frameworks**: Streamlit, FastAPI
- **Data Processing**: pandas, numpy, matplotlib, seaborn
- **Automation**: n8n workflow automation
- **APIs**: Yahoo Finance API, Discord API
- **Protocols**: Model Context Protocol (MCP)
- **Tools**: VS Code, Git, Docker

## License

All code and content in this repository is for educational and personal use.

---

*Somesh Ramesh Ghaturle*  
*MS in Data Science, Pace University*
