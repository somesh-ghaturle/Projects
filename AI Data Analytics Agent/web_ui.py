"""web_ui.py
Professional Streamlit entrypoint for the AI Data Analytics Agent.

This file is a thin wrapper around `analytics_core.OllamaAnalyticsAgent` and
defines a small Streamlit interface locally so the module imports cleanly.

Run with:
  streamlit run web_ui.py
"""

import os
import streamlit as st
from analytics_core import OllamaAnalyticsAgent


class StreamlitInterface:
    def __init__(self):
        self.agent = None
        self.data = None

    def run(self):
        st.set_page_config(page_title="AI Data Analytics Agent", page_icon="📊", layout="wide")
        st.title("🤖 AI Data Analytics Agent with Ollama")
        st.markdown("*Powered by local Ollama models*")

        # Sidebar
        with st.sidebar:
            st.header("Configuration")
            try:
                available_models = __import__('ollama').list()
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
                if model_names:
                    selected_model = st.selectbox("Select Ollama Model", model_names)
                else:
                    st.error("No Ollama models found. Please pull a model first.")
                    selected_model = None
            except Exception as e:
                st.error(f"Cannot connect to Ollama: {e}")
                st.info("Make sure Ollama is running: `ollama serve`")
                selected_model = None

            if st.button("Initialize Agent"):
                if selected_model:
                    st.session_state.agent = OllamaAnalyticsAgent(selected_model)
                    st.success(f"Agent initialized with {selected_model}")
                else:
                    st.error("Cannot initialize agent: No model selected or available.")

        # Data upload
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader("Choose a data file", type=['csv', 'xlsx', 'json'])
        agent = st.session_state.get('agent', None)
        data = st.session_state.get('data', None)
        if uploaded_file and agent:
            os.makedirs("data", exist_ok=True)
            file_path = os.path.join("data", f"temp_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            with st.spinner("Loading and analyzing data..."):
                data = agent.load_and_analyze_data(file_path)
                if data is not None:
                    st.session_state.data = data
                    st.success(f"Data loaded successfully: {data.shape[0]} rows, {data.shape[1]} columns")

        if data is not None and agent is not None:
            st.subheader("📋 Data Preview")
            st.dataframe(data.head())
            st.header("🔍 Analysis Options")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📈 Descriptive Analytics"):
                    result = agent.descriptive_analytics(data)
                    self._display_result(result)
                if st.button("🔮 Predictive Analytics"):
                    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                    target_col = st.selectbox("Select target column", numeric_cols)
                    result = agent.predictive_analytics(data, target_col)
                    self._display_result(result)
            with col2:
                if st.button("🧹 Data Cleaning Suggestions"):
                    result = agent.data_cleaning_suggestions(data)
                    self._display_result(result)
                if st.button("📊 Visualization Suggestions"):
                    result = agent.visualization_suggestions(data)
                    self._display_result(result)

            st.header("💬 Custom Analysis")
            custom_query = st.text_area("Ask a custom question about your data:")
            if st.button("🤔 Analyze Query") and custom_query:
                result = agent.custom_analysis(data, custom_query)
                self._display_result(result)

    def _display_result(self, result):
        st.subheader(f"📊 {result.analysis_type.title()} Analysis Results")
        st.markdown("### 🧠 AI Insights")
        st.write(result.insights)
        if result.visualizations:
            st.markdown("### 📈 Visualizations")
            for viz in result.visualizations:
                st.plotly_chart(viz['figure'], use_container_width=True)
                st.caption(viz.get('description', ''))
        with st.expander("📋 Raw Analysis Results"):
            st.json(result.results)


def main():
    interface = StreamlitInterface()
    interface.run()


if __name__ == '__main__':
    main()
