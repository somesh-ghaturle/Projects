# Personal Learning Projects Repository

This repository contains my personal learning projects developed during my Master's degree in Data Science at Pace University.

## Overview

- Each subfolder represents a different project or experiment completed as part of coursework, self-study, or exploration in data science, machine learning, and AI.
- Projects may include code, documentation, and sample data.

## Notable Projects

- **AI Data Analytics Agent**: An AI-powered analytics tool using Streamlit and Ollama for local LLM-based data analysis.

---

# AI Data Analytics Agent (Ollama + Streamlit)

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

## License

All code and content in this repository is for educational and personal use.

---

*Somesh Ramesh Ghaturle*
*MS in Data Science, Pace University*
