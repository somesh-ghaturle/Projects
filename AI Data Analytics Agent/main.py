import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Ollama Integration
import ollama

# Set Ollama host
os.environ["OLLAMA_HOST"] = "http://localhost:11434"

@dataclass
class AnalysisResult:
    """Structure for analysis results"""
    analysis_type: str
    results: Dict[str, Any]
    insights: str
    visualizations: List[Dict] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class OllamaAnalyticsAgent:
    """Enhanced AI Data Analytics Agent using Ollama local models"""
    
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        self.conversation_history = []
        self.data_cache = {}
        
        # Verify Ollama connection
        try:
            available_models = ollama.list()
            print(f"[DEBUG] ollama.list() response: {available_models}")
            # Defensive: handle both list and dict response
            models = []
            if isinstance(available_models, dict) and 'models' in available_models:
                models = available_models['models']
            elif hasattr(available_models, 'models'):
                models = available_models.models
            elif isinstance(available_models, list):
                models = available_models
            else:
                print("[ERROR] Unexpected response format from ollama.list().")
            model_names = []
            for model in models:
                if hasattr(model, 'model'):
                    model_names.append(model.model)
                elif isinstance(model, dict) and 'name' in model:
                    model_names.append(model['name'])
                elif isinstance(model, str):
                    model_names.append(model)
                else:
                    print(f"[ERROR] Model entry missing 'model' or 'name': {model}")
            if model_name not in model_names:
                print(f"Warning: Model '{model_name}' not found. Available models: {model_names}")
                if model_names:
                    self.model_name = model_names[0]
                    print(f"Using '{self.model_name}' instead.")
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            print("Make sure Ollama is running with: ollama serve")
    
    def ask_ollama_stream(self, prompt: str, context: str = None) -> str:
        """Enhanced Ollama interaction with context and error handling"""
        import streamlit as st
        # Build enhanced prompt with context
        enhanced_prompt = self._build_enhanced_prompt(prompt, context)
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=enhanced_prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_predict': 2048,
                }
            )
            # st.info(f"[DEBUG] Ollama response: {response}")
            full_response = response.get('response', None)
            if not full_response:
                st.error(f"[ERROR] Ollama returned no 'response' field. Raw: {response}")
                return "[ERROR] Ollama returned no 'response' field."
            # Store in conversation history
            self.conversation_history.append({
                'prompt': prompt,
                'response': full_response,
                'timestamp': datetime.now().isoformat()
            })
            return full_response
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            st.error(error_msg)
            return error_msg

    def _build_enhanced_prompt(self, user_prompt: str, context: str = None) -> str:
        """Build enhanced prompt with context and instructions"""
        
        system_prompt = """You are an expert data analyst AI assistant. Your responses should be:
        1. Accurate and data-driven
        2. Clear and actionable
        3. Include specific insights and recommendations
        4. Mention relevant statistical methods when applicable
        5. Suggest appropriate visualizations
        
        When analyzing data, always consider:
        - Data quality and completeness
        - Statistical significance
        - Business implications
        - Potential limitations
        """
        
        if context:
            enhanced_prompt = f"{system_prompt}\n\nData Context:\n{context}\n\nUser Question: {user_prompt}\n\nProvide a comprehensive analysis:"
        else:
            enhanced_prompt = f"{system_prompt}\n\nUser Question: {user_prompt}\n\nProvide a comprehensive analysis:"
        
        return enhanced_prompt

# ... rest of the file is identical to streamlit_app.py ...
