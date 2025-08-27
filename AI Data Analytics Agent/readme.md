# AI Data Analytics Agent (Ollama + Streamlit)

> Intelligent data analytics platform powered by local LLMs and Streamlit for comprehensive data analysis workflows

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=f## 👨‍💻 Author & License

All code and content in this repository is for educational and personal use.

**Somesh Ramesh Ghaturle**  
MS in Data Science, Pace University

📧 **Email:** [someshghaturle@gmail.com](mailto:someshghaturle@gmail.com)  
🐙 **GitHub:** [https://github.com/somesh-ghaturle](https://github.com/somesh-ghaturle)  
💼 **LinkedIn:** [https://www.linkedin.com/in/someshghaturle/](https://www.linkedin.com/in/someshghaturle/)go=Streamlit&logoColor=white)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=flat&logo=llama&logoColor=white)](https://ollama.ai/)

## Overview

This app is an AI-powered data analytics tool that leverages local LLMs via Ollama and provides an intuitive Streamlit web interface for comprehensive data analysis workflows. Perfect for data scientists, analysts, and researchers who need powerful, privacy-focused analytics capabilities.

## 📚 Table of Contents

- [🏗️ System Architecture](#️-system-architecture)
- [🔄 Analytics Workflow](#-analytics-workflow)
- [🤖 AI Processing Pipeline](#-ai-processing-pipeline)
- [📁 Project Structure](#-project-structure)
- [🎯 Features Overview](#-features-overview)
- [⚙️ Installation & Usage](#️-installation--usage)

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        A[Streamlit Web App]
        B[File Upload Interface]
        C[Analytics Dashboard]
        D[Visualization Panel]
    end
    
    subgraph "Data Processing Layer"
        E[Data Loader]
        F[Data Validator]
        G[Data Cleaner]
        H[Feature Engineer]
    end
    
    subgraph "AI Analytics Engine"
        I[Ollama LLM Server]
        J[Analytics Agent]
        K[Visualization Agent]
        L[Insights Generator]
    end
    
    subgraph "Analytics Modules"
        M[Descriptive Analytics]
        N[Predictive Analytics]
        O[Data Cleaning]
        P[Visualization Engine]
    end
    
    subgraph "Data Storage"
        Q[(Local File System)]
        R[Session State]
        S[Cache Layer]
    end
    
    A --> B
    B --> E
    E --> F
    F --> G
    G --> H
    
    H --> J
    J --> I
    I --> L
    L --> M
    L --> N
    L --> O
    L --> P
    
    M --> C
    N --> C
    O --> C
    P --> D
    
    E --> Q
    F --> R
    G --> S
    
    style I fill:#ff9999
    style J fill:#ff9999
    style A fill:#99ccff
    style C fill:#99ccff
    style Q fill:#99ff99
```

## 🔄 Analytics Workflow

```mermaid
flowchart TD
    START([User Opens App]) --> UPLOAD{File Upload}
    
    UPLOAD -->|CSV| PARSE_CSV[Parse CSV Data]
    UPLOAD -->|Excel| PARSE_EXCEL[Parse Excel Data]
    UPLOAD -->|JSON| PARSE_JSON[Parse JSON Data]
    
    PARSE_CSV --> VALIDATE[Data Validation]
    PARSE_EXCEL --> VALIDATE
    PARSE_JSON --> VALIDATE
    
    VALIDATE --> VALID{Data Valid?}
    VALID -->|No| ERROR[Show Error Message]
    VALID -->|Yes| PREVIEW[Data Preview]
    
    ERROR --> UPLOAD
    PREVIEW --> SELECT{Select Analytics Type}
    
    SELECT -->|Descriptive| DESC[Descriptive Analytics]
    SELECT -->|Predictive| PRED[Predictive Analytics]
    SELECT -->|Cleaning| CLEAN[Data Cleaning]
    SELECT -->|Visualization| VIZ[Data Visualization]
    
    DESC --> AI_DESC[AI Analysis Engine]
    PRED --> AI_PRED[AI Prediction Engine]
    CLEAN --> AI_CLEAN[AI Cleaning Engine]
    VIZ --> AI_VIZ[AI Visualization Engine]
    
    AI_DESC --> INSIGHTS[Generate Insights]
    AI_PRED --> INSIGHTS
    AI_CLEAN --> INSIGHTS
    AI_VIZ --> INSIGHTS
    
    INSIGHTS --> DISPLAY[Display Results]
    DISPLAY --> EXPORT{Export Results?}
    
    EXPORT -->|Yes| SAVE[Save Analysis]
    EXPORT -->|No| NEW{New Analysis?}
    
    SAVE --> NEW
    NEW -->|Yes| SELECT
    NEW -->|No| END([Session Complete])
    
    style START fill:#90EE90
    style END fill:#90EE90
    style ERROR fill:#FFB6C1
    style AI_DESC fill:#DDA0DD
    style AI_PRED fill:#DDA0DD
    style AI_CLEAN fill:#DDA0DD
    style AI_VIZ fill:#DDA0DD
```

## 🤖 AI Processing Pipeline

```mermaid
sequenceDiagram
    participant User
    participant Streamlit as Streamlit App
    participant Processor as Data Processor
    participant Ollama as Ollama LLM
    participant Engine as Analytics Engine
    participant Display as Result Display
    
    User->>Streamlit: Upload Data File
    Streamlit->>Processor: Process File
    
    Note over Processor: Data Validation & Cleaning
    Processor->>Streamlit: Processed Data
    
    User->>Streamlit: Select Analytics Type
    Streamlit->>Engine: Initialize Analysis
    
    Engine->>Ollama: Send Analysis Request
    Note over Ollama: Local LLM Processing
    Ollama->>Engine: Return Analysis
    
    Engine->>Processor: Apply Transformations
    Processor->>Engine: Processed Results
    
    Engine->>Display: Format Results
    Display->>Streamlit: Render Output
    Streamlit->>User: Show Analysis Results
    
    Note over User,Display: Interactive Analytics Session
```

## 📁 Project Structure

```bash
AI Data Analytics Agent/
│
├── 📋 Documentation
│   ├── README.md                           # This file
│   ├── AI Data Analytics Agent Documentation.pdf
│   └── requirements.txt                    # Python dependencies
│
├── 🤖 Core Application
│   └── Final Ai Agent.py                   # Main Streamlit application
│
├── 🔧 Configuration
│   ├── .streamlit/                         # Streamlit configuration (if exists)
│   └── config/                            # App configuration files (if exists)
│
├── 📊 Data Processing Modules
│   ├── data_loader.py                     # Data loading utilities (embedded)
│   ├── data_cleaner.py                    # Data cleaning functions (embedded)
│   └── visualization.py                   # Chart generation (embedded)
│
├── 🧠 AI Analytics Engine
│   ├── ollama_client.py                   # Ollama integration (embedded)
│   ├── analytics_agent.py                # Analytics processing (embedded)
│   └── insights_generator.py             # Insights generation (embedded)
│
└── 💾 Data & Cache
    ├── uploads/                           # Temporary uploaded files
    ├── cache/                            # Session cache
    └── exports/                          # Generated reports
```

## 🎯 Features Overview

```mermaid
mindmap
  root((AI Analytics Agent))
    Data Upload
      CSV Files
      Excel Files
      JSON Files
      Drag & Drop
    Analytics Types
      Descriptive
        Summary Statistics
        Data Profiling
        Missing Values
        Correlations
      Predictive
        Trend Analysis
        Forecasting
        ML Predictions
        Pattern Recognition
      Cleaning
        Missing Data
        Outlier Detection
        Data Transformation
        Quality Assessment
      Visualization
        Charts & Graphs
        Interactive Plots
        Custom Dashboards
        Export Options
    AI Capabilities
      Local LLM Processing
      Natural Language Insights
      Automated Analysis
      Intelligent Recommendations
    User Experience
      Web Interface
      Real-time Processing
      Interactive Results
      Export Functionality
```

## ⚙️ Installation & Usage

### Prerequisites

- Python 3.8+
- Ollama installed and running locally
- Required Python packages (see requirements.txt)

### Setup Instructions

1. **Install Ollama**

   ```sh
   # macOS
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama service
   ollama serve
   ```

2. **Pull a Language Model**

   ```sh
   # Pull a lightweight model (recommended)
   ollama pull llama2:7b
   
   # Or pull other models
   ollama pull codellama
   ```

3. **Install Python Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Application**

   ```sh
   streamlit run "Final Ai Agent.py"
   ```

5. **Access the App**

   ```sh
   # Open in browser
   http://localhost:8501
   ```

### Usage Workflow

1. **Start the Application** - Launch the Streamlit app
2. **Upload Your Data** - Drag and drop CSV, Excel, or JSON files
3. **Choose Analytics Type** - Select from descriptive, predictive, cleaning, or visualization
4. **AI Processing** - Let the local LLM analyze your data
5. **Review Results** - Examine insights, charts, and recommendations
6. **Export Analysis** - Save results for future reference

### Key Features

- Upload CSV, Excel, or JSON data
- AI-powered descriptive and predictive analytics
- Automated data cleaning and quality assessment
- Interactive visualizations and dashboards
- Natural language insights generation
- Privacy-focused local processing

### Important Notes

- Ollama must be running locally for the app to work
- Ensure you have sufficient RAM for the chosen LLM model
- Large datasets may take longer to process
- All data processing happens locally for privacy

### Troubleshooting

- **Ollama connection error:** Make sure `ollama serve` is running and the model is pulled
- **Memory issues:** Try using a smaller LLM model or reduce dataset size
- **Import errors:** Verify all dependencies are installed with `pip install -r requirements.txt`
- **Port conflicts:** Check if port 8501 is available or specify a different port

## �‍💻 Author & License

All code and content in this repository is for educational and personal use.

**Somesh Ramesh Ghaturle**  
MS in Data Science, Pace University

---

### Built with ❤️ using Streamlit, Ollama, and Python
