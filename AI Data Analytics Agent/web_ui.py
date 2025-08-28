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

        # --- Custom styling for a more professional look ---
        st.markdown(
            """
            <style>
            .app-header {display:flex;align-items:center;gap:12px}
            .app-title {font-size:28px;font-weight:700;margin:0}
            .app-sub {color: #6c757d; margin:0}
            .stButton>button {background-color:#0b5cff;color:white}
            .card {background:#ffffff;border-radius:8px;padding:18px;box-shadow:0 1px 3px rgba(16,24,40,0.05);}
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Header
        with st.container():
            cols = st.columns([0.08, 0.92])
            with cols[0]:
                st.markdown("<div style='font-size:40px'>📊</div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown("<div class='app-header'><div><h1 class='app-title'>AI Data Analytics Agent</h1><div class='app-sub'>Professional analytics powered by local Ollama models</div></div></div>", unsafe_allow_html=True)

        # Sidebar configuration
        with st.sidebar:
            st.header("Configuration")
            st.markdown("Choose model and initialize the analytics agent.")
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
                    # Prefer llama3.2 if present
                    # allow override via env var
                    preferred_env = os.environ.get('OLLAMA_PREFERRED_MODEL')
                    preferred = None
                    if preferred_env:
                        for m in model_names:
                            if preferred_env in m:
                                preferred = m
                                break
                    if not preferred:
                        for m in model_names:
                            if 'llama3.2' in m or 'llama3' in m:
                                preferred = m
                                break
                    if preferred:
                        ordered = [preferred] + [x for x in model_names if x != preferred]
                    else:
                        ordered = model_names
                    selected_model = st.selectbox("Select Ollama Model", ordered)
                else:
                    selected_model = None
                    st.warning("No Ollama models found. Pull a model or start Ollama.")
            except Exception as e:
                selected_model = None
                st.error(f"Cannot connect to Ollama: {e}")
                st.info("Make sure Ollama is running: `ollama serve`")

            if st.button("Initialize Agent"):
                if selected_model:
                    st.session_state.agent = OllamaAnalyticsAgent(selected_model)
                    st.success(f"Agent initialized with {selected_model}")
                else:
                    st.error("Cannot initialize agent: No model selected or available.")
            # Auto-initialize if a preferred model is available and agent not yet initialized
            try:
                if 'agent' not in st.session_state and selected_model is not None:
                    # auto-init when a preferred model exists
                    st.session_state.agent = OllamaAnalyticsAgent(selected_model)
                    st.success(f"Agent auto-initialized with {selected_model}")
            except Exception:
                # don't crash UI when auto-init fails
                pass

        # Data upload
        st.markdown("## 📁 Data Upload")
        uploaded_file = st.file_uploader("Choose a data file", type=['csv', 'xlsx', 'json'])
        agent = st.session_state.get('agent', None)
        data = st.session_state.get('data', None)

        if uploaded_file and agent:
            # Choose a writable upload directory. In production `./data` may be mounted read-only.
            upload_dir = os.environ.get("APP_UPLOAD_DIR")
            if not upload_dir:
                # Prefer a temp directory inside the container; fall back to ./data only if /tmp isn't usable.
                try:
                    upload_dir = "/tmp/app_uploads"
                    os.makedirs(upload_dir, exist_ok=True)
                except Exception:
                    # Last-resort fallback for local development when ./data is writable.
                    os.makedirs("data", exist_ok=True)
                    upload_dir = "data"
            else:
                os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, f"temp_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            with st.spinner("Loading and analyzing data..."):
                data = agent.load_and_analyze_data(file_path)
                if data is not None:
                    st.session_state.data = data
                    # Intentionally silent on successful load to avoid verbose UI messages
                else:
                    # show loading/parsing errors from the agent if present
                    load_err = agent.data_cache.get('load_error') if hasattr(agent, 'data_cache') else None
                    if load_err:
                        st.error(f"Failed to load file: {load_err}")
                    else:
                        st.error("Failed to load file: unknown error")

        if data is not None and agent is not None:
            st.subheader("📋 Data Preview")
            st.dataframe(data.head())

            # Main analysis tabs for a cleaner UX
            tabs = st.tabs(["Descriptive", "Predictive", "Cleaning", "Visualizations", "Custom"])

            with tabs[0]:
                st.markdown("### 📈 Descriptive Analytics")
                if st.button("Run Descriptive Analysis", key='desc'):
                    with st.spinner("Running descriptive analytics..."):
                        result = agent.descriptive_analytics(data)
                    self._display_result(result)

            with tabs[1]:
                st.markdown("### 🔮 Predictive Analytics")
                numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                if numeric_cols:
                    target_col = st.selectbox("Select target column", numeric_cols, key='target')
                    if st.button("Run Predictive Analysis", key='pred'):
                        with st.spinner("Running predictive analytics..."):
                            result = agent.predictive_analytics(data, target_col)
                        self._display_result(result)
                else:
                    st.info("No numeric columns found for predictive analytics.")

            with tabs[2]:
                st.markdown("### 🧹 Data Cleaning Suggestions")
                if st.button("Get Cleaning Suggestions", key='clean'):
                    with st.spinner("Assessing data quality..."):
                        result = agent.data_cleaning_suggestions(data)
                    self._display_result(result)

            with tabs[3]:
                st.markdown("### 📊 Visualization Suggestions")
                if st.button("Get Visualization Suggestions", key='viz'):
                    with st.spinner("Preparing visualizations..."):
                        result = agent.visualization_suggestions(data)
                    self._display_result(result)

            with tabs[4]:
                st.markdown("### 💬 Custom Analysis")
                custom_query = st.text_area("Ask a custom question about your data:")
                if st.button("Analyze Query", key='custom'):
                    if not custom_query or not custom_query.strip():
                        st.warning("Please enter a query before clicking Analyze.")
                    else:
                        try:
                            with st.spinner("Running custom analysis..."):
                                result = agent.custom_analysis(data, custom_query)
                            if isinstance(result, Exception):
                                st.error(f"Custom analysis failed: {result}")
                            else:
                                if isinstance(result.insights, str) and result.insights.startswith("[ERROR]"):
                                    st.warning(f"Analysis completed with warning: {result.insights}")
                                self._display_result(result)
                        except Exception as e:
                            st.exception(e)

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
