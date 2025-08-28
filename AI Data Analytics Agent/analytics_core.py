"""
analytics_core.py
Refactored core analytics module extracted from the previous `app.py`.

This module exposes:
- AnalysisResult
- OllamaAnalyticsAgent

It is import-safe (does not call Ollama at import time) so it can be imported
by UI modules without side-effects.
"""

import os
import pandas as pd
import numpy as np
import json
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import time

# Local LLM client
import ollama

# Set default Ollama host (can be overridden via env)
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")

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
		self.conversation_history: List[Dict[str, Any]] = []
		self.data_cache: Dict[str, Any] = {}

		# Note: do not raise on import-time failures; just log and continue.
		try:
			available_models = ollama.list()
			models = []
			if isinstance(available_models, dict) and 'models' in available_models:
				models = available_models['models']
			elif hasattr(available_models, 'models'):
				models = available_models.models
			elif isinstance(available_models, list):
				models = available_models
			model_names = []
			for model in models:
				if hasattr(model, 'model'):
					model_names.append(model.model)
				elif isinstance(model, dict) and 'name' in model:
					model_names.append(model['name'])
				elif isinstance(model, str):
					model_names.append(model)
			if model_name not in model_names and model_names:
				# fall back to first available model
				self.model_name = model_names[0]
		except Exception:
			# If Ollama is not reachable at init, we defer errors until a call is made.
			pass

	def ask_ollama_stream(self, prompt: str, context: str = None) -> str:
		"""Call Ollama with a composed prompt; returns text or error string."""
		enhanced_prompt = self._build_enhanced_prompt(prompt, context)
		try:
			# Use a short prediction budget for interactive requests
			options = {
				'temperature': 0.7,
				'top_p': 0.9,
				'num_predict': 512,
			}

			# Execute in a worker with a timeout to avoid blocking callers
			import concurrent.futures

			def _gen():
				return ollama.generate(model=self.model_name, prompt=enhanced_prompt, options=options)

			with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
				future = executor.submit(_gen)
				try:
					t0 = time.time()
					response = future.result(timeout=30)
					t1 = time.time()
					self.data_cache['last_ollama_time'] = t1 - t0
				except concurrent.futures.TimeoutError:
					future.cancel()
					self.data_cache['last_ollama_time'] = None
					return "[ERROR] Ollama timeout"

			full_response = response.get('response', None)
			if not full_response:
				return "[ERROR] Ollama returned no 'response' field."

			# store conversation
			self.conversation_history.append({
				'prompt': prompt,
				'response': full_response,
				'timestamp': datetime.now().isoformat(),
				'ollama_time': self.data_cache.get('last_ollama_time')
			})
			return full_response
		except Exception as e:
			return f"[ERROR] Error communicating with Ollama: {e}"

	def _build_enhanced_prompt(self, user_prompt: str, context: str = None) -> str:
		system_prompt = (
			"You are an expert data analyst AI assistant. Your responses should be:\n"
			"1. Accurate and data-driven\n"
			"2. Clear and actionable\n"
			"3. Include specific insights and recommendations\n"
			"4. Mention relevant statistical methods when applicable\n"
			"5. Suggest appropriate visualizations\n\n"
			"When analyzing data, always consider:\n- Data quality and completeness\n- Statistical significance\n- Business implications\n- Potential limitations\n"
		)
		if context:
			return f"{system_prompt}\n\nData Context:\n{context}\n\nUser Question: {user_prompt}\n\nProvide a comprehensive analysis:"
		return f"{system_prompt}\n\nUser Question: {user_prompt}\n\nProvide a comprehensive analysis:"

	def load_and_analyze_data(self, file_path: str) -> pd.DataFrame:
		"""Load a dataset from CSV/Excel/JSON and cache a lightweight summary."""
		try:
			low = file_path.lower()
			if low.endswith('.csv'):
				data = pd.read_csv(file_path)
			elif low.endswith('.xlsx') or low.endswith('.xls'):
				# prefer openpyxl engine when available
				try:
					data = pd.read_excel(file_path, engine='openpyxl')
				except Exception:
					# fallback to default engine
					data = pd.read_excel(file_path)
			elif low.endswith('.json'):
				try:
					data = pd.read_json(file_path)
				except ValueError:
					# try treating as ndjson / lines
					data = pd.read_json(file_path, lines=True)
			else:
				raise ValueError("Unsupported file format. Use CSV, Excel, or JSON.")

			self.data_cache['current_data'] = data
			self.data_cache['data_summary'] = self._generate_data_summary(data)
			return data
		except Exception as e:
			# record a load error for the UI to display
			try:
				self.data_cache['load_error'] = str(e)
			except Exception:
				# ignore cache write failures
				pass
			return None

	def _generate_data_summary(self, data: pd.DataFrame) -> str:
		parts = []
		parts.append(f"Dataset shape: {data.shape[0]} rows, {data.shape[1]} columns")
		numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
		categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
		datetime_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
		parts.append(f"Numeric columns ({len(numeric_cols)}): {numeric_cols}")
		parts.append(f"Categorical columns ({len(categorical_cols)}): {categorical_cols}")
		if datetime_cols:
			parts.append(f"DateTime columns ({len(datetime_cols)}): {datetime_cols}")
		missing_info = data.isnull().sum()
		if missing_info.sum() > 0:
			parts.append(f"Missing values: {missing_info[missing_info > 0].to_dict()}")
		parts.append(f"Sample data:\n{data.head(3).to_string()}")
		if len(numeric_cols) > 0:
			parts.append(f"Numeric summary:\n{data[numeric_cols].describe().to_string()}")
		return "\n".join(parts)

	# Descriptive, predictive, cleaning and visualization helper methods
	# (copied from the original implementation)
	def descriptive_analytics(self, data: pd.DataFrame) -> AnalysisResult:
		MAX_ROWS = 20000
		SAMPLE_ROWS = 5000
		if data.shape[0] > MAX_ROWS:
			used = data.sample(n=SAMPLE_ROWS, random_state=42)
			self.data_cache['analysis_used_sample'] = True
		else:
			used = data

		stats_summary = self._generate_statistical_summary(used)

		prompt = f"""Analyze this dataset and provide comprehensive descriptive insights:\n\nStatistical Summary:\n{stats_summary}\n\nPlease provide:\n1. Key characteristics of the data\n2. Distribution patterns\n3. Notable outliers or anomalies\n4. Data quality assessment\n5. Recommendations for further analysis\n"""

		insights = self.ask_ollama_stream(prompt, self.data_cache.get('data_summary', ''))
		t_vis0 = time.time()
		visualizations = self._create_descriptive_visualizations(used)
		t_vis1 = time.time()
		self.data_cache['last_visualization_time'] = t_vis1 - t_vis0

		results = {
			'statistical_summary': stats_summary,
			'timings': {
				'ollama_seconds': self.data_cache.get('last_ollama_time'),
				'visualization_seconds': self.data_cache.get('last_visualization_time')
			}
		}
		return AnalysisResult(analysis_type='descriptive', results=results, insights=insights, visualizations=visualizations)

	def _generate_statistical_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
		summary = {}
		numeric_cols = data.select_dtypes(include=[np.number]).columns
		if len(numeric_cols) > 0:
			summary['numeric_stats'] = data[numeric_cols].describe().to_dict()
			if len(numeric_cols) > 1:
				summary['correlations'] = data[numeric_cols].corr().to_dict()
			outliers = {}
			for col in numeric_cols:
				Q1 = data[col].quantile(0.25)
				Q3 = data[col].quantile(0.75)
				IQR = Q3 - Q1
				outliers[col] = len(data[(data[col] < (Q1 - 1.5 * IQR)) | (data[col] > (Q3 + 1.5 * IQR))])
			summary['outliers'] = outliers
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
		visualizations = []
		numeric_cols = data.select_dtypes(include=[np.number]).columns
		import plotly.express as px
		import plotly.graph_objects as go
		from plotly.subplots import make_subplots

		if len(numeric_cols) > 1:
			fig_corr = px.imshow(data[numeric_cols].corr(), title='Correlation Matrix', color_continuous_scale='RdBu', aspect='auto')
			visualizations.append({'type': 'correlation_heatmap', 'figure': fig_corr, 'description': 'Correlation between numeric variables'})

		if len(numeric_cols) > 0:
			fig_dist = make_subplots(rows=min(3, len(numeric_cols)), cols=min(2, len(numeric_cols)), subplot_titles=[f"Distribution of {col}" for col in numeric_cols[:6]])
			for i, col in enumerate(numeric_cols[:6]):
				row = i // 2 + 1
				col_pos = i % 2 + 1
				fig_dist.add_trace(go.Histogram(x=data[col], name=col, showlegend=False), row=row, col=col_pos)
			fig_dist.update_layout(title='Distribution of Numeric Variables', height=600)
			visualizations.append({'type': 'distributions', 'figure': fig_dist, 'description': 'Distribution patterns of numeric variables'})

		return visualizations

	def predictive_analytics(self, data: pd.DataFrame, target_column: str = None) -> AnalysisResult:
		if target_column is None:
			numeric_cols = data.select_dtypes(include=[np.number]).columns
			if len(numeric_cols) > 0:
				target_column = data[numeric_cols].var().idxmax()

		trends = self._analyze_trends(data, target_column)
		prompt = f"""Based on this dataset, provide predictive insights:\n\nTarget Variable: {target_column}\nTrend Analysis: {trends}\n\nPlease provide:\n1. Predictive patterns identified\n2. Key predictive features\n3. Potential forecasting approach\n4. Risk factors and limitations\n5. Recommendations for predictive modeling\n"""
		insights = self.ask_ollama_stream(prompt, self.data_cache.get('data_summary', ''))
		visualizations = self._create_predictive_visualizations(data, target_column)
		return AnalysisResult(analysis_type='predictive', results={'trends': trends, 'target_column': target_column}, insights=insights, visualizations=visualizations)

	def _analyze_trends(self, data: pd.DataFrame, target_column: str) -> Dict[str, Any]:
		import numpy as np
		from scipy import stats
		trends = {}
		if target_column and target_column in data.columns:
			trends['basic_stats'] = {'mean': data[target_column].mean(), 'std': data[target_column].std(), 'trend': 'increasing' if data[target_column].iloc[-1] > data[target_column].iloc[0] else 'decreasing'}
			date_cols = data.select_dtypes(include=['datetime64']).columns
			if len(date_cols) > 0:
				data_sorted = data.sort_values(date_cols[0])
				x = np.arange(len(data_sorted))
				y = data_sorted[target_column].values
				slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
				trends['temporal_trend'] = {'slope': slope, 'r_squared': r_value**2, 'p_value': p_value, 'trend_strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.3 else 'weak'}
		return trends

	def _create_predictive_visualizations(self, data: pd.DataFrame, target_column: str) -> List[Dict]:
		visualizations = []
		import plotly.express as px
		if target_column and target_column in data.columns:
			date_cols = data.select_dtypes(include=['datetime64']).columns
			if len(date_cols) > 0:
				fig_ts = px.line(data.sort_values(date_cols[0]), x=date_cols[0], y=target_column, title=f"Time Series: {target_column}")
				visualizations.append({'type': 'time_series', 'figure': fig_ts, 'description': f'Temporal trend of {target_column}'})
			numeric_cols = data.select_dtypes(include=[np.number]).columns
			if len(numeric_cols) > 1:
				correlations = data[numeric_cols].corr()[target_column].drop(target_column).abs().sort_values(ascending=True)
				fig_importance = px.bar(x=correlations.values, y=correlations.index, orientation='h', title=f"Feature Importance (Correlation with {target_column})")
				visualizations.append({'type': 'feature_importance', 'figure': fig_importance, 'description': 'Correlation-based feature importance'})
		return visualizations

	def data_cleaning_suggestions(self, data: pd.DataFrame) -> AnalysisResult:
		quality_issues = self._assess_data_quality(data)
		prompt = f"""Analyze this dataset for data quality issues and provide cleaning recommendations:\n\nData Quality Issues Detected:\n{json.dumps(quality_issues, indent=2)}\n\nPlease provide:\n1. Priority ranking of issues to address\n2. Specific cleaning steps for each issue\n3. Potential risks of each cleaning approach\n4. Data validation recommendations\n5. Best practices for maintaining data quality\n"""
		insights = self.ask_ollama_stream(prompt, self.data_cache.get('data_summary', ''))
		return AnalysisResult(analysis_type='data_cleaning', results={'quality_issues': quality_issues}, insights=insights)

	def _assess_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
		issues = {}
		missing_counts = data.isnull().sum()
		if missing_counts.sum() > 0:
			issues['missing_values'] = missing_counts[missing_counts > 0].to_dict()
		duplicate_count = data.duplicated().sum()
		if duplicate_count > 0:
			issues['duplicate_rows'] = duplicate_count
		type_issues = {}
		for col in data.columns:
			if data[col].dtype == 'object':
				numeric_conversion = pd.to_numeric(data[col], errors='coerce')
				if not numeric_conversion.isnull().all() and numeric_conversion.isnull().sum() < len(data) * 0.5:
					type_issues[col] = "potentially_numeric"
		if type_issues:
			issues['type_inconsistencies'] = type_issues
		numeric_cols = data.select_dtypes(include=[np.number]).columns
		outlier_info = {}
		for col in numeric_cols:
			Q1 = data[col].quantile(0.25)
			Q3 = data[col].quantile(0.75)
			IQR = Q3 - Q1
			outliers = data[(data[col] < (Q1 - 1.5 * IQR)) | (data[col] > (Q3 + 1.5 * IQR))]
			if len(outliers) > 0:
				outlier_info[col] = {'count': len(outliers), 'percentage': len(outliers) / len(data) * 100}
		if outlier_info:
			issues['outliers'] = outlier_info
		return issues

	def visualization_suggestions(self, data: pd.DataFrame) -> AnalysisResult:
		viz_analysis = self._analyze_visualization_needs(data)
		prompt = f"""Based on this dataset characteristics, recommend the best visualizations:\n\nDataset Analysis for Visualization:\n{json.dumps(viz_analysis, indent=2)}\n\nPlease provide:\n1. Most appropriate chart types for each variable\n2. Recommended multi-variable visualizations\n3. Interactive visualization opportunities\n4. Dashboard layout suggestions\n5. Specific insights each visualization would reveal\n"""
		insights = self.ask_ollama_stream(prompt, self.data_cache.get('data_summary', ''))
		sample_visualizations = self._create_sample_visualizations(data)
		return AnalysisResult(analysis_type='visualization', results={'viz_analysis': viz_analysis}, insights=insights, visualizations=sample_visualizations)

	def _analyze_visualization_needs(self, data: pd.DataFrame) -> Dict[str, Any]:
		numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
		categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
		datetime_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
		analysis = {'column_types': {'numeric': len(numeric_cols), 'categorical': len(categorical_cols), 'datetime': len(datetime_cols)}}
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
		data_size = len(data)
		if data_size > 10000:
			analysis['size_considerations'] = 'large_dataset_optimizations_needed'
		elif data_size < 100:
			analysis['size_considerations'] = 'small_dataset_simple_charts'
		return analysis

	def _create_sample_visualizations(self, data: pd.DataFrame) -> List[Dict]:
		visualizations = []
		numeric_cols = data.select_dtypes(include=[np.number]).columns
		categorical_cols = data.select_dtypes(include=['object', 'category']).columns
		import plotly.express as px
		if len(numeric_cols) >= 2:
			fig_scatter = px.scatter(data, x=numeric_cols[0], y=numeric_cols[1], title=f"Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}")
			visualizations.append({'type': 'scatter_plot', 'figure': fig_scatter, 'description': 'Sample scatter plot showing relationship between variables'})
		if len(categorical_cols) > 0:
			value_counts = data[categorical_cols[0]].value_counts().head(10)
			fig_bar = px.bar(x=value_counts.index, y=value_counts.values, title=f"Distribution of {categorical_cols[0]}")
			visualizations.append({'type': 'bar_chart', 'figure': fig_bar, 'description': f'Distribution of categories in {categorical_cols[0]}'})
		return visualizations

	def custom_analysis(self, data: pd.DataFrame, query: str) -> AnalysisResult:
		relevant_stats = self._generate_query_relevant_stats(data, query)
		enhanced_prompt = f"""User Query: {query}\n\nRelevant Statistics:\n{json.dumps(relevant_stats, indent=2)}\n\nPlease provide a comprehensive analysis addressing the user's specific question with:\n1. Direct answer to the query\n2. Supporting statistical evidence\n3. Relevant insights and patterns\n4. Actionable recommendations\n5. Potential limitations or caveats\n"""
		insights = self.ask_ollama_stream(enhanced_prompt, self.data_cache.get('data_summary', ''))
		visualizations = self._create_query_visualizations(data, query)
		return AnalysisResult(analysis_type='custom', results={'relevant_stats': relevant_stats, 'query': query}, insights=insights, visualizations=visualizations)

	def _generate_query_relevant_stats(self, data: pd.DataFrame, query: str) -> Dict[str, Any]:
		stats = {'basic_info': {'shape': data.shape, 'columns': data.columns.tolist()}}
		query_lower = query.lower()
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
				stats['temporal_info'] = {'date_range': [str(data[datetime_cols[0]].min()), str(data[datetime_cols[0]].max())], 'date_columns': datetime_cols.tolist()}
		return stats

	def _create_query_visualizations(self, data: pd.DataFrame, query: str) -> List[Dict]:
		visualizations = []
		query_lower = query.lower()
		if any(word in query_lower for word in ['correlation', 'relationship']):
			numeric_cols = data.select_dtypes(include=[np.number]).columns
			if len(numeric_cols) > 1:
				import plotly.express as px
				fig_corr = px.imshow(data[numeric_cols].corr(), title='Correlation Matrix', color_continuous_scale='RdBu')
				visualizations.append({'type': 'correlation', 'figure': fig_corr, 'description': 'Correlation matrix based on your query'})
		return visualizations
