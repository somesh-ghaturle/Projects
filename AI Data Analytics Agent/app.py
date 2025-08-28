"""
Deprecated `app.py` placeholder.
The analytics implementation has been moved to `analytics_core.py` and the
Streamlit entrypoint is `web_ui.py`.

If you need the original full source, see `docs/legacy/app.orig.py`.
"""

from analytics_core import OllamaAnalyticsAgent, AnalysisResult, StreamlitInterface

__all__ = ["OllamaAnalyticsAgent", "AnalysisResult", "StreamlitInterface"]
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
import time

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
            # Run ollama.generate in a thread with a timeout to avoid blocking the UI indefinitely.
            import concurrent.futures
            options = {
                'temperature': 0.7,
                'top_p': 0.9,
                # Reduce token prediction to speed up responses in interactive mode
                'num_predict': 512,
            }
            def _gen():
                return ollama.generate(model=self.model_name, prompt=enhanced_prompt, options=options)

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_gen)
                try:
                    t0 = time.time()
                    response = future.result(timeout=30)  # 30s timeout for Ollama
                    t1 = time.time()
                    self.data_cache['last_ollama_time'] = t1 - t0
                except concurrent.futures.TimeoutError:
                    future.cancel()
                    st.error("Ollama request timed out (30s). Try with a smaller dataset or run locally with more resources.")
                    self.data_cache['last_ollama_time'] = None
                    return "[ERROR] Ollama timeout"
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
            # Also store last response time in conversation history for quick access
            try:
                self.conversation_history[-1]['ollama_time'] = self.data_cache.get('last_ollama_time')
            except Exception:
                pass
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
    
    def load_and_analyze_data(self, file_path: str) -> pd.DataFrame:
        """Load data with comprehensive analysis"""
        try:
            # Load data based on file extension
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                try:
                    # Explicitly use openpyxl engine for Excel files
                    import openpyxl
                    data = pd.read_excel(file_path, engine='openpyxl')
                except ImportError:
                    print("❌ Error: The openpyxl package is required for Excel files.")
                    print("Installing openpyxl...")
                    import subprocess
                    subprocess.check_call(["pip", "install", "openpyxl"])
                    print("Retrying with openpyxl...")
                    data = pd.read_excel(file_path, engine='openpyxl')
                except Exception as excel_error:
                    print(f"❌ Excel-specific error: {str(excel_error)}")
                    raise
            elif file_path.endswith('.json'):
                data = pd.read_json(file_path)
            else:
                raise ValueError("Unsupported file format. Use CSV, Excel, or JSON.")
            
            # Cache the data
            self.data_cache['current_data'] = data
            
            # Generate data summary for context
            data_summary = self._generate_data_summary(data)
            self.data_cache['data_summary'] = data_summary
            
            print(f"✅ Data loaded successfully: {data.shape[0]} rows, {data.shape[1]} columns")
            return data
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return None
    
    def _generate_data_summary(self, data: pd.DataFrame) -> str:
        """Generate comprehensive data summary for AI context"""
        
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Dataset shape: {data.shape[0]} rows, {data.shape[1]} columns")
        
        # Column information
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
        
        summary_parts.append(f"Numeric columns ({len(numeric_cols)}): {numeric_cols}")
        summary_parts.append(f"Categorical columns ({len(categorical_cols)}): {categorical_cols}")
        if datetime_cols:
            summary_parts.append(f"DateTime columns ({len(datetime_cols)}): {datetime_cols}")
        
        # Missing values
        missing_info = data.isnull().sum()
        if missing_info.sum() > 0:
            missing_cols = missing_info[missing_info > 0].to_dict()
            summary_parts.append(f"Missing values: {missing_cols}")
        
        # Sample data
        summary_parts.append(f"Sample data:\n{data.head(3).to_string()}")
        
        # Basic statistics for numeric columns
        if len(numeric_cols) > 0:
            summary_parts.append(f"Numeric summary:\n{data[numeric_cols].describe().to_string()}")
        
        return "\n".join(summary_parts)
    
    def descriptive_analytics(self, data: pd.DataFrame) -> AnalysisResult:
        """Enhanced descriptive analytics with visualizations"""
        
        context = self.data_cache.get('data_summary', '')
        
        # Generate statistical analysis
        # If dataset is large, sample to speed up analysis and visualizations
        MAX_ROWS = 20000
        SAMPLE_ROWS = 5000
        if data.shape[0] > MAX_ROWS:
            sampled_data = data.sample(n=SAMPLE_ROWS, random_state=42)
            stats_summary = self._generate_statistical_summary(sampled_data)
            used_data = sampled_data
            self.data_cache['analysis_used_sample'] = True
        else:
            stats_summary = self._generate_statistical_summary(data)
            used_data = data
        
        prompt = f"""Analyze this dataset and provide comprehensive descriptive insights:

Statistical Summary:
{stats_summary}

Please provide:
1. Key characteristics of the data
2. Distribution patterns
3. Notable outliers or anomalies
4. Data quality assessment
5. Recommendations for further analysis
"""
        
        insights = self.ask_ollama_stream(prompt, context)

        # Generate visualizations (time this step)
        t_vis0 = time.time()
        visualizations = self._create_descriptive_visualizations(used_data)
        t_vis1 = time.time()
        vis_time = t_vis1 - t_vis0
        self.data_cache['last_visualization_time'] = vis_time

        results = {
            "statistical_summary": stats_summary,
            "timings": {
                "ollama_seconds": self.data_cache.get('last_ollama_time'),
                "visualization_seconds": self.data_cache.get('last_visualization_time')
            }
        }

        return AnalysisResult(
            analysis_type="descriptive",
            results=results,
            insights=insights,
            visualizations=visualizations
        )
    
    def _generate_statistical_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive statistical summary"""
        
        summary = {}
        
        # Numeric columns analysis
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary['numeric_stats'] = data[numeric_cols].describe().to_dict()
            
            # Correlation matrix
            if len(numeric_cols) > 1:
                summary['correlations'] = data[numeric_cols].corr().to_dict()
            
            # Outlier detection using IQR
            outliers = {}
            for col in numeric_cols:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                outlier_count = len(data[(data[col] < (Q1 - 1.5 * IQR)) | (data[col] > (Q3 + 1.5 * IQR))])
                outliers[col] = outlier_count
            summary['outliers'] = outliers
        
        # Categorical columns analysis
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            cat_summary = {}
            for col in categorical_cols:
                cat_summary[col] = {
                    'unique_count': data[col].nunique(),
                    'most_frequent': data[col].mode().iloc[0] if len(data[col].mode()) > 0 else None,
                    'value_counts': data[col].value_counts().head().to_dict()
                }
            summary['categorical_stats'] = cat_summary
        
        return summary
    
    def _create_descriptive_visualizations(self, data: pd.DataFrame) -> List[Dict]:
        """Create descriptive visualizations"""
        
        visualizations = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        # Correlation heatmap
        if len(numeric_cols) > 1:
            fig_corr = px.imshow(
                data[numeric_cols].corr(),
                title="Correlation Matrix",
                color_continuous_scale="RdBu",
                aspect="auto"
            )
            visualizations.append({
                'type': 'correlation_heatmap',
                'figure': fig_corr,
                'description': 'Correlation between numeric variables'
            })
        
        # Distribution plots for numeric columns
        if len(numeric_cols) > 0:
            fig_dist = make_subplots(
                rows=min(3, len(numeric_cols)),
                cols=min(2, len(numeric_cols)),
                subplot_titles=[f"Distribution of {col}" for col in numeric_cols[:6]]
            )
            
            for i, col in enumerate(numeric_cols[:6]):
                row = i // 2 + 1
                col_pos = i % 2 + 1
                
                fig_dist.add_trace(
                    go.Histogram(x=data[col], name=col, showlegend=False),
                    row=row, col=col_pos
                )
            
            fig_dist.update_layout(title="Distribution of Numeric Variables", height=600)
            visualizations.append({
                'type': 'distributions',
                'figure': fig_dist,
                'description': 'Distribution patterns of numeric variables'
            })
        
        return visualizations
    
    def predictive_analytics(self, data: pd.DataFrame, target_column: str = None) -> AnalysisResult:
        """Enhanced predictive analytics"""
        
        context = self.data_cache.get('data_summary', '')
        
        # Identify potential target variables if not specified
        if target_column is None:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                # Use the column with highest variance as default target
                target_column = data[numeric_cols].var().idxmax()
        
        # Generate trend analysis
        trends = self._analyze_trends(data, target_column)
        
        prompt = f"""Based on this dataset, provide predictive insights:

Target Variable: {target_column}
Trend Analysis: {trends}

Please provide:
1. Predictive patterns identified
2. Key predictive features
3. Potential forecasting approach
4. Risk factors and limitations
5. Recommendations for predictive modeling
"""
        
        insights = self.ask_ollama_stream(prompt, context)
        
        # Generate predictive visualizations
        visualizations = self._create_predictive_visualizations(data, target_column)
        
        return AnalysisResult(
            analysis_type="predictive",
            results={"trends": trends, "target_column": target_column},
            insights=insights,
            visualizations=visualizations
        )
    
    def _analyze_trends(self, data: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """Analyze trends in the data"""
        
        trends = {}
        
        if target_column and target_column in data.columns:
            # Basic trend statistics
            trends['basic_stats'] = {
                'mean': data[target_column].mean(),
                'std': data[target_column].std(),
                'trend': 'increasing' if data[target_column].iloc[-1] > data[target_column].iloc[0] else 'decreasing'
            }
            
            # If there's a time component, analyze temporal trends
            date_cols = data.select_dtypes(include=['datetime64']).columns
            if len(date_cols) > 0:
                date_col = date_cols[0]
                # Sort by date and calculate trend
                data_sorted = data.sort_values(date_col)
                # Simple linear trend
                x = np.arange(len(data_sorted))
                y = data_sorted[target_column].values
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                trends['temporal_trend'] = {
                    'slope': slope,
                    'r_squared': r_value**2,
                    'p_value': p_value,
                    'trend_strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.3 else 'weak'
                }
        
        return trends
    
    def _create_predictive_visualizations(self, data: pd.DataFrame, target_column: str) -> List[Dict]:
        """Create predictive visualizations"""
        
        visualizations = []
        
        if target_column and target_column in data.columns:
            # Time series plot if date column exists
            date_cols = data.select_dtypes(include=['datetime64']).columns
            if len(date_cols) > 0:
                fig_ts = px.line(
                    data.sort_values(date_cols[0]),
                    x=date_cols[0],
                    y=target_column,
                    title=f"Time Series: {target_column}"
                )
                visualizations.append({
                    'type': 'time_series',
                    'figure': fig_ts,
                    'description': f'Temporal trend of {target_column}'
                })
            
            # Feature importance (correlation with target)
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                correlations = data[numeric_cols].corr()[target_column].drop(target_column).abs().sort_values(ascending=True)
                
                fig_importance = px.bar(
                    x=correlations.values,
                    y=correlations.index,
                    orientation='h',
                    title=f"Feature Importance (Correlation with {target_column})"
                )
                visualizations.append({
                    'type': 'feature_importance',
                    'figure': fig_importance,
                    'description': 'Correlation-based feature importance'
                })
        
        return visualizations
    
    def data_cleaning_suggestions(self, data: pd.DataFrame) -> AnalysisResult:
        """Enhanced data cleaning analysis"""
        
        context = self.data_cache.get('data_summary', '')
        
        # Generate data quality assessment
        quality_issues = self._assess_data_quality(data)
        
        prompt = f"""Analyze this dataset for data quality issues and provide cleaning recommendations:

Data Quality Issues Detected:
{json.dumps(quality_issues, indent=2)}

Please provide:
1. Priority ranking of issues to address
2. Specific cleaning steps for each issue
3. Potential risks of each cleaning approach
4. Data validation recommendations
5. Best practices for maintaining data quality
"""
        
        insights = self.ask_ollama_stream(prompt, context)
        
        return AnalysisResult(
            analysis_type="data_cleaning",
            results={"quality_issues": quality_issues},
            insights=insights
        )
    
    def _assess_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive data quality assessment"""
        
        issues = {}
        
        # Missing values
        missing_counts = data.isnull().sum()
        if missing_counts.sum() > 0:
            issues['missing_values'] = missing_counts[missing_counts > 0].to_dict()
        
        # Duplicate rows
        duplicate_count = data.duplicated().sum()
        if duplicate_count > 0:
            issues['duplicate_rows'] = duplicate_count
        
        # Data type inconsistencies
        type_issues = {}
        for col in data.columns:
            # Check if numeric columns have non-numeric values
            if data[col].dtype == 'object':
                # Try to convert to numeric
                numeric_conversion = pd.to_numeric(data[col], errors='coerce')
                if not numeric_conversion.isnull().all() and numeric_conversion.isnull().sum() < len(data) * 0.5:
                    type_issues[col] = "potentially_numeric"
        
        if type_issues:
            issues['type_inconsistencies'] = type_issues
        
        # Outliers in numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        outlier_info = {}
        for col in numeric_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = data[(data[col] < (Q1 - 1.5 * IQR)) | (data[col] > (Q3 + 1.5 * IQR))]
            if len(outliers) > 0:
                outlier_info[col] = {
                    'count': len(outliers),
                    'percentage': len(outliers) / len(data) * 100
                }
        
        if outlier_info:
            issues['outliers'] = outlier_info
        
        return issues
    
    def visualization_suggestions(self, data: pd.DataFrame) -> AnalysisResult:
        """Enhanced visualization recommendations"""
        
        context = self.data_cache.get('data_summary', '')
        
        # Analyze data characteristics for visualization
        viz_analysis = self._analyze_visualization_needs(data)
        
        prompt = f"""Based on this dataset characteristics, recommend the best visualizations:

Dataset Analysis for Visualization:
{json.dumps(viz_analysis, indent=2)}

Please provide:
1. Most appropriate chart types for each variable
2. Recommended multi-variable visualizations
3. Interactive visualization opportunities
4. Dashboard layout suggestions
5. Specific insights each visualization would reveal
"""
        
        insights = self.ask_ollama_stream(prompt, context)
        
        # Generate sample visualizations
        sample_visualizations = self._create_sample_visualizations(data)
        
        return AnalysisResult(
            analysis_type="visualization",
            results={"viz_analysis": viz_analysis},
            insights=insights,
            visualizations=sample_visualizations
        )
    
    def _analyze_visualization_needs(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data for visualization recommendations"""
        
        analysis = {}
        
        # Column types and characteristics
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
        
        analysis['column_types'] = {
            'numeric': len(numeric_cols),
            'categorical': len(categorical_cols),
            'datetime': len(datetime_cols)
        }
        
        # Suggested chart types
        chart_suggestions = []
        
        if len(numeric_cols) >= 2:
            chart_suggestions.extend(['scatter_plot', 'correlation_heatmap'])
        
        if len(categorical_cols) > 0:
            chart_suggestions.extend(['bar_chart', 'pie_chart'])
        
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            chart_suggestions.append('time_series')
        
        if len(numeric_cols) > 0:
            chart_suggestions.extend(['histogram', 'box_plot'])
        
        analysis['recommended_charts'] = chart_suggestions
        
        # Data size considerations
        data_size = len(data)
        if data_size > 10000:
            analysis['size_considerations'] = 'large_dataset_optimizations_needed'
        elif data_size < 100:
            analysis['size_considerations'] = 'small_dataset_simple_charts'
        
        return analysis
    
    def _create_sample_visualizations(self, data: pd.DataFrame) -> List[Dict]:
        """Create sample visualizations"""
        
        visualizations = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        # Sample scatter plot
        if len(numeric_cols) >= 2:
            fig_scatter = px.scatter(
                data,
                x=numeric_cols[0],
                y=numeric_cols[1],
                title=f"Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}"
            )
            visualizations.append({
                'type': 'scatter_plot',
                'figure': fig_scatter,
                'description': 'Sample scatter plot showing relationship between variables'
            })
        
        # Sample bar chart
        if len(categorical_cols) > 0:
            value_counts = data[categorical_cols[0]].value_counts().head(10)
            fig_bar = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"Distribution of {categorical_cols[0]}"
            )
            visualizations.append({
                'type': 'bar_chart',
                'figure': fig_bar,
                'description': f'Distribution of categories in {categorical_cols[0]}'
            })
        
        return visualizations
    
    def custom_analysis(self, data: pd.DataFrame, query: str) -> AnalysisResult:
        """Enhanced custom analysis with context"""
        
        context = self.data_cache.get('data_summary', '')
        
        # Generate relevant statistics based on query
        relevant_stats = self._generate_query_relevant_stats(data, query)
        
        enhanced_prompt = f"""User Query: {query}

Relevant Statistics:
{json.dumps(relevant_stats, indent=2)}

Please provide a comprehensive analysis addressing the user's specific question with:
1. Direct answer to the query
2. Supporting statistical evidence
3. Relevant insights and patterns
4. Actionable recommendations
5. Potential limitations or caveats
"""
        
        insights = self.ask_ollama_stream(enhanced_prompt, context)
        
        # Generate query-specific visualizations
        visualizations = self._create_query_visualizations(data, query)
        
        return AnalysisResult(
            analysis_type="custom",
            results={"relevant_stats": relevant_stats, "query": query},
            insights=insights,
            visualizations=visualizations
        )
    
    def _generate_query_relevant_stats(self, data: pd.DataFrame, query: str) -> Dict[str, Any]:
        """Generate statistics relevant to the user query"""
        
        stats = {}
        query_lower = query.lower()
        
        # Basic stats always included
        stats['basic_info'] = {
            'shape': data.shape,
            'columns': data.columns.tolist()
        }
        
        # Query-specific statistics
        if any(word in query_lower for word in ['correlation', 'relationship', 'association']):
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                stats['correlations'] = data[numeric_cols].corr().to_dict()
        
        if any(word in query_lower for word in ['distribution', 'histogram', 'spread']):
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                stats['distributions'] = data[numeric_cols].describe().to_dict()
        
        if any(word in query_lower for word in ['trend', 'time', 'temporal']):
            datetime_cols = data.select_dtypes(include=['datetime64']).columns
            if len(datetime_cols) > 0:
                stats['temporal_info'] = {
                    'date_range': [str(data[datetime_cols[0]].min()), str(data[datetime_cols[0]].max())],
                    'date_columns': datetime_cols.tolist()
                }
        
        return stats
    
    def _create_query_visualizations(self, data: pd.DataFrame, query: str) -> List[Dict]:
        """Create visualizations based on user query"""
        
        visualizations = []
        query_lower = query.lower()
        
        # Correlation-related visualizations
        if any(word in query_lower for word in ['correlation', 'relationship']):
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                fig_corr = px.imshow(
                    data[numeric_cols].corr(),
                    title="Correlation Matrix",
                    color_continuous_scale="RdBu"
                )
                visualizations.append({
                    'type': 'correlation',
                    'figure': fig_corr,
                    'description': 'Correlation matrix based on your query'
                })
        
        return visualizations

class StreamlitInterface:
    """Streamlit web interface for the analytics agent"""
    
    def __init__(self):
        self.agent = None
        self.data = None
    
    def run(self):
        st.set_page_config(
            page_title="AI Data Analytics Agent",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("🤖 AI Data Analytics Agent with Ollama")
        st.markdown("*Powered by local Ollama models*")
        
        # Sidebar for configuration
        with st.sidebar:
            st.header("Configuration")
            # Model selection
            try:
                available_models = ollama.list()
                st.write(f"[DEBUG] ollama.list() response: {available_models}")
                models = []
                if isinstance(available_models, dict) and 'models' in available_models:
                    models = available_models['models']
                elif hasattr(available_models, 'models'):
                    models = available_models.models
                elif isinstance(available_models, list):
                    models = available_models
                else:
                    st.error("[ERROR] Unexpected response format from ollama.list().")
                model_names = []
                for model in models:
                    if hasattr(model, 'model'):
                        model_names.append(model.model)
                    elif isinstance(model, dict) and 'name' in model:
                        model_names.append(model['name'])
                    elif isinstance(model, str):
                        model_names.append(model)
                    else:
                        st.error(f"[ERROR] Model entry missing 'model' or 'name': {model}")
                if model_names:
                    selected_model = st.selectbox("Select Ollama Model", model_names)
                else:
                    st.error("No Ollama models found. Please pull a model first.")
                    st.code("ollama pull llama3")
                    selected_model = None
            except Exception as e:
                st.error(f"Cannot connect to Ollama: {e}")
                st.info("Make sure Ollama is running: `ollama serve`")
                selected_model = None
            # Initialize agent
            if st.button("Initialize Agent"):
                if selected_model:
                    st.session_state.agent = OllamaAnalyticsAgent(selected_model)
                    st.success(f"Agent initialized with {selected_model}")
                else:
                    st.error("Cannot initialize agent: No model selected or available.")
        
        # File upload
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Choose a data file",
            type=['csv', 'xlsx', 'json'],
            help="Upload your dataset for analysis"
        )
        agent = st.session_state.get('agent', None)
        data = st.session_state.get('data', None)
        if uploaded_file and agent:
            try:
                # Ensure data directory exists
                os.makedirs("data", exist_ok=True)
                
                # Save uploaded file to data directory
                file_path = os.path.join("data", f"temp_{uploaded_file.name}")
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Check if it's an Excel file and show a note about openpyxl
                if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                    st.info("Loading Excel file... Make sure openpyxl is installed.")
                
                # Load data
                with st.spinner("Loading and analyzing data..."):
                    data = agent.load_and_analyze_data(file_path)
                    if data is not None:
                        st.session_state.data = data
                        st.success(f"Data loaded successfully: {data.shape[0]} rows, {data.shape[1]} columns")
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                if "openpyxl" in str(e).lower():
                    st.info("To fix this issue, install openpyxl: `pip install openpyxl`")
                import traceback
                st.expander("Error details").code(traceback.format_exc())
                
        if data is not None and agent is not None:
            # Display data preview
            st.subheader("📋 Data Preview")
            st.dataframe(data.head())
            # Analysis options
            st.header("🔍 Analysis Options")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📈 Descriptive Analytics"):
                    self._run_analysis("descriptive")
                if st.button("🔮 Predictive Analytics"):
                    target_col = st.selectbox(
                        "Select target column",
                        data.select_dtypes(include=[np.number]).columns
                    )
                    self._run_analysis("predictive", target_column=target_col)
            with col2:
                if st.button("🧹 Data Cleaning Suggestions"):
                    self._run_analysis("cleaning")
                if st.button("📊 Visualization Suggestions"):
                    self._run_analysis("visualization")
            # Custom query
            st.header("💬 Custom Analysis")
            custom_query = st.text_area(
                "Ask a custom question about your data:",
                placeholder="e.g., What's the correlation between sales and marketing spend?"
            )
            if st.button("🤔 Analyze Query") and custom_query:
                self._run_analysis("custom", query=custom_query)
    
    def _run_analysis(self, analysis_type: str, **kwargs):
        """Run analysis and display results"""
        
        agent = st.session_state.get('agent', None)
        data = st.session_state.get('data', None)
        if not agent or data is None:
            st.error("Please initialize agent and upload data first.")
            return
        
        with st.spinner(f"Running {analysis_type} analysis..."):
            try:
                if analysis_type == "descriptive":
                    result = agent.descriptive_analytics(data)
                elif analysis_type == "predictive":
                    result = agent.predictive_analytics(data, kwargs.get('target_column'))
                elif analysis_type == "cleaning":
                    result = agent.data_cleaning_suggestions(data)
                elif analysis_type == "visualization":
                    result = agent.visualization_suggestions(data)
                elif analysis_type == "custom":
                    result = agent.custom_analysis(data, kwargs.get('query'))
                
                # Display results
                st.subheader(f"📊 {result.analysis_type.title()} Analysis Results")
                
                # Show AI insights
                st.markdown("### 🧠 AI Insights")
                st.write(result.insights)
                
                # Show visualizations if available
                if result.visualizations:
                    st.markdown("### 📈 Visualizations")
                    for viz in result.visualizations:
                        st.plotly_chart(viz['figure'], use_container_width=True)
                        st.caption(viz['description'])
                
                # Show raw results in expander
                with st.expander("📋 Raw Analysis Results"):
                    st.json(result.results)
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

def main():
    """Main function to run the application"""
    
    # Check if running in Streamlit
    try:
        # If streamlit is available and we're in a streamlit context
        interface = StreamlitInterface()
        interface.run()
    except:
        # Fallback to CLI interface
        print("🤖 AI Data Analytics Agent with Ollama")
        print("=" * 50)
        
        # Initialize agent
        print("Available models:")
        try:
            models = ollama.list()
            for i, model in enumerate(models['models']):
                print(f"{i+1}. {model['name']}")
            
            choice = input("\nSelect model number (or press Enter for llama3): ")
            if choice.strip():
                model_name = models['models'][int(choice)-1]['name']
            else:
                model_name = "llama3"
                
        except Exception as e:
            print(f"Error accessing Ollama: {e}")
            model_name = "llama3"
        
        agent = OllamaAnalyticsAgent(model_name)
        
        # Load data
        file_path = input("Enter path to your data file: ")
        data = agent.load_and_analyze_data(file_path)
        
        if data is None:
            return
        
        # CLI menu
        while True:
            print("\n" + "="*50)
            print("Select an analysis option:")
            print("1. 📈 Descriptive Analytics")
            print("2. 🔮 Predictive Analytics")
            print("3. 🧹 Data Cleaning Suggestions")
            print("4. 📊 Visualization Suggestions")
            print("5. 💬 Custom Query")
            print("6. 🔄 Load New Data")
            print("7. 📜 View Conversation History")
            print("8. ❌ Exit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                result = agent.descriptive_analytics(data)
                print(f"\n📊 DESCRIPTIVE ANALYSIS:\n{result.insights}")
                
            elif choice == "2":
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    print(f"Available numeric columns: {list(numeric_cols)}")
                    target = input("Enter target column (or press Enter for auto-selection): ").strip()
                    target = target if target else None
                else:
                    target = None
                
                result = agent.predictive_analytics(data, target)
                print(f"\n🔮 PREDICTIVE ANALYSIS:\n{result.insights}")
                
            elif choice == "3":
                result = agent.data_cleaning_suggestions(data)
                print(f"\n🧹 DATA CLEANING SUGGESTIONS:\n{result.insights}")
                
            elif choice == "4":
                result = agent.visualization_suggestions(data)
                print(f"\n📊 VISUALIZATION SUGGESTIONS:\n{result.insights}")
                
            elif choice == "5":
                query = input("Ask a question about your data: ")
                result = agent.custom_analysis(data, query)
                print(f"\n💬 CUSTOM ANALYSIS:\n{result.insights}")
                
            elif choice == "6":
                file_path = input("Enter path to new data file: ")
                new_data = agent.load_and_analyze_data(file_path)
                if new_data is not None:
                    data = new_data
                
            elif choice == "7":
                print("\n📜 CONVERSATION HISTORY:")
                for i, conv in enumerate(agent.conversation_history[-5:], 1):
                    print(f"\n{i}. Query: {conv['prompt'][:100]}...")
                    print(f"   Time: {conv['timestamp']}")
                
            elif choice == "8":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
