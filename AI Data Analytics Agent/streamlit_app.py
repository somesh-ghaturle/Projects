"""
This file was archived. The original implementation is stored at
`docs/legacy/streamlit_app.orig.py`.

Please use the new entrypoint: `web_ui.py`.
Run with:
    streamlit run web_ui.py
"""

if __name__ == '__main__':
    print("This file has been archived. Run: streamlit run web_ui.py")
"""
This file has been archived. The original implementation is stored at
`docs/legacy/streamlit_app.orig.py`.

Please use the new entrypoint: `web_ui.py`.
Run with:
    streamlit run web_ui.py
"""

if __name__ == '__main__':
        print("This file has been archived. Run: streamlit run web_ui.py")
    
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
        stats_summary = self._generate_statistical_summary(data)
        
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
        
        # Generate visualizations
        visualizations = self._create_descriptive_visualizations(data)
        
        return AnalysisResult(
            analysis_type="descriptive",
            results={"statistical_summary": stats_summary},
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
            # Save uploaded file
            file_path = f"temp_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            # Load data
            data = agent.load_and_analyze_data(file_path)
            st.session_state.data = data
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
                # Inform user if a sample was used for analysis
                try:
                    if getattr(agent, 'data_cache', {}).get('analysis_used_sample'):
                        st.warning("Note: Dataset was large; analysis used a 5,000-row random sample to speed up results.")
                except Exception:
                    pass
                
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
