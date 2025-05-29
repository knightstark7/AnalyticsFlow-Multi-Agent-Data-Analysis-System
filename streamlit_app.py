import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import asyncio
import threading
import queue
import time
from typing import Dict, Any
import io
import sys
import json

# Import project modules
from logger import setup_logger
from langchain_core.messages import HumanMessage

from load_cfg import OPENAI_API_KEY, LANGCHAIN_API_KEY, WORKING_DIRECTORY
from core.workflow import WorkflowManager
from core.language_models import LanguageModelManager

# Page configuration
st.set_page_config(
    page_title="🤖 AnalyticsFlow - Multi-Agent Data Analysis System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    
    .status-processing {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitMultiAgentSystem:
    def __init__(self):
        self.logger = setup_logger()
        self.setup_environment()
        self.lm_manager = LanguageModelManager()
        self.workflow_manager = WorkflowManager(
            language_models=self.lm_manager.get_models(),
            working_directory=WORKING_DIRECTORY
        )
        
    def setup_environment(self):
        """Initialize environment variables"""
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "AnalyticsFlow Multi-Agent System"

        if not os.path.exists(WORKING_DIRECTORY):
            os.makedirs(WORKING_DIRECTORY)
            self.logger.info(f"Created working directory: {WORKING_DIRECTORY}")
    
    def run_analysis(self, user_input: str, progress_callback=None):
        """Run the multi-agent system with progress tracking"""
        try:
            graph = self.workflow_manager.get_graph()
            
            # Create initial message with proper validation
            try:
                initial_message = HumanMessage(content=user_input)
            except Exception as msg_error:
                self.logger.error(f"Error creating initial message: {str(msg_error)}")
                # Fallback to dict format with proper type
                initial_message = {"type": "human", "content": user_input}
            
            initial_state = {
                "messages": [initial_message],
                "hypothesis": "",
                "process_decision": "",
                "process": "",
                "visualization_state": "",
                "searcher_state": "",
                "code_state": "",
                "report_section": "",
                "quality_review": "",
                "needs_revision": False,
                "last_sender": "",
            }
            
            events = graph.stream(
                initial_state,
                {"configurable": {"thread_id": "1"}, "recursion_limit": 3000},
                stream_mode="values",
                debug=False
            )
            
            results = []
            for event in events:
                try:
                    # Validate and fix messages in event before processing
                    if "messages" in event and event["messages"]:
                        fixed_messages = []
                        for msg in event["messages"]:
                            if isinstance(msg, dict):
                                # Ensure dict messages have required fields
                                if "content" in msg:
                                    if "type" not in msg:
                                        msg["type"] = "ai"  # Default type for missing type
                                    elif msg.get("type") not in ["human", "ai", "system"]:
                                        msg["type"] = "ai"  # Fix invalid types
                                    # Ensure name field exists for AI messages
                                    if msg["type"] == "ai" and "name" not in msg:
                                        msg["name"] = "assistant"
                                else:
                                    # Skip messages without content
                                    continue
                            fixed_messages.append(msg)
                        event["messages"] = fixed_messages
                    
                    if progress_callback:
                        progress_callback(event)
                    results.append(event)
                    
                except Exception as event_error:
                    self.logger.error(f"Error processing event: {str(event_error)}")
                    # Continue processing despite individual event errors
                    continue
                
            return results
            
        except Exception as e:
            self.logger.error(f"Error running analysis: {str(e)}")
            return None

def safe_json_parse(text):
    """Safely parse JSON with fallback handling"""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try to extract JSON from text if it's embedded
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            try:
                return json.loads(text[start:end])
            except:
                pass
        # Return the original text if parsing fails
        return text

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AnalyticsFlow - Multi-Agent Data Analysis System</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'system' not in st.session_state:
        st.session_state.system = StreamlitMultiAgentSystem()
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    
    if 'current_status' not in st.session_state:
        st.session_state.current_status = "ready"
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Key Features")
        
        # Agent status overview
        st.markdown("### 🤖 Agent Status")
        agents = [
            ("📊 Process Agent", "Coordination & supervision"),
            ("🔍 Search Agent", "Information retrieval"),
            ("📈 Visualization Agent", "Chart creation"),
            ("💻 Code Agent", "Code writing & execution"),
            ("📝 Report Agent", "Report generation"),
            ("✅ Quality Review Agent", "Quality assurance"),
            ("🔧 Refiner Agent", "Result refinement"),
            ("💡 Hypothesis Agent", "Hypothesis development"),
            ("📋 Note Agent", "Notes & summaries")
        ]
        
        for agent_name, description in agents:
            st.markdown(f"""
            <div class="agent-card">
                <strong>{agent_name}</strong><br>
                <small>{description}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 📁 Data Upload")
        
        # Data upload section
        uploaded_file = st.file_uploader(
            "Choose CSV file for analysis",
            type=['csv'],
            help="Upload a CSV file containing data for analysis"
        )
        
        if uploaded_file is not None:
            # Save uploaded file
            file_path = os.path.join(WORKING_DIRECTORY, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Display file info
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Preview data
            try:
                df = pd.read_csv(file_path)
                st.markdown("### 👀 Data Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                # Basic statistics
                st.markdown("### 📊 Basic Statistics")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                
                with col_stat1:
                    st.metric("Rows", len(df))
                with col_stat2:
                    st.metric("Columns", len(df.columns))
                with col_stat3:
                    st.metric("Size (MB)", f"{uploaded_file.size / (1024*1024):.2f}")
                with col_stat4:
                    st.metric("Missing Data", df.isnull().sum().sum())
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        # Analysis input section
        st.markdown("## 🎯 Analysis Requirements")
        
        # Pre-defined analysis templates
        analysis_templates = {
            "General Analysis": "Perform comprehensive data analysis to find important patterns and insights",
            "Trend Analysis": "Analyze time trends and predict future trends",
            "Customer Segmentation": "Segment customers based on purchasing behavior and characteristics",
            "Sales Performance": "Evaluate sales performance across time, products, and channels",
            "Custom": "Enter custom analysis requirements"
        }
        
        selected_template = st.selectbox(
            "Choose analysis type:",
            list(analysis_templates.keys()),
            help="Select a pre-defined analysis template or customize your own"
        )
        
        if selected_template == "Custom":
            user_input = st.text_area(
                "Enter your analysis requirements:",
                placeholder="Example: Use machine learning to analyze sales data and create comprehensive reports with charts",
                height=100
            )
        else:
            user_input = analysis_templates[selected_template]
            st.text_area("Analysis requirements:", value=user_input, height=100, disabled=True)
        
        # Add data path if file is uploaded
        if uploaded_file is not None:
            user_input = f"datapath:{uploaded_file.name}\n{user_input}"
        
        # Analysis execution
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            if not user_input.strip():
                st.error("Please enter analysis requirements!")
            else:
                st.session_state.current_status = "processing"
                
                # Create progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("Analyzing data..."):
                    def progress_callback(event):
                        # Update progress based on event
                        if "last_sender" in event:
                            sender = event.get("last_sender", "")
                            status_text.markdown(f"🔄 Processing: {sender}")
                    
                    try:
                        results = st.session_state.system.run_analysis(user_input, progress_callback)
                        
                        if results:
                            st.session_state.analysis_results = results
                            st.session_state.current_status = "completed"
                            progress_bar.progress(100)
                            status_text.markdown("✅ Analysis completed!")
                            st.success("🎉 Analysis completed! See results below.")
                        else:
                            st.session_state.current_status = "error"
                            st.error("❌ Error occurred during analysis.")
                            
                    except Exception as e:
                        st.session_state.current_status = "error"
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.markdown("## 📊 System Status")
        
        # System status
        if st.session_state.current_status == "ready":
            st.markdown('<div class="status-success">🟢 Ready</div>', unsafe_allow_html=True)
        elif st.session_state.current_status == "processing":
            st.markdown('<div class="status-processing">🟡 Processing</div>', unsafe_allow_html=True)
        elif st.session_state.current_status == "completed":
            st.markdown('<div class="status-success">🟢 Completed</div>', unsafe_allow_html=True)
        elif st.session_state.current_status == "error":
            st.markdown('<div class="status-error">🔴 Error</div>', unsafe_allow_html=True)
        
        # System info
        st.markdown("### ℹ️ System Information")
        st.markdown(f"**Working Directory:** `{WORKING_DIRECTORY}`")
        st.markdown(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Help section
        st.markdown("### 💡 Usage Guide")
        st.markdown("""
        1. **Upload Data**: Choose CSV file containing data for analysis
        2. **Choose Analysis Type**: Use pre-defined template or customize your own
        3. **Start Analysis**: Click "Start Analysis" button
        4. **See Results**: Track progress and see results
        """)
        
        # Quick stats
        if st.session_state.analysis_results:
            st.markdown("### 📈 Analysis Statistics")
            st.metric("Processing Steps", len(st.session_state.analysis_results))
    
    # Results section
    if st.session_state.analysis_results:
        st.markdown("## 📋 Analysis Results")
        
        # Create tabs for different result views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "💬 Details", "📁 Files", "📈 Visualizations"])
        
        with tab1:
            st.markdown("### 📊 Summary Results")
            
            # Display key insights from the last result
            if st.session_state.analysis_results:
                last_result = st.session_state.analysis_results[-1]
                
                if "messages" in last_result and last_result["messages"]:
                    last_message = last_result["messages"][-1]
                    try:
                        if hasattr(last_message, 'content'):
                            st.markdown("#### 🎯 Final Result:")
                            st.markdown(last_message.content)
                        elif isinstance(last_message, dict) and "content" in last_message:
                            st.markdown("#### 🎯 Final Result:")
                            st.markdown(last_message["content"])
                        else:
                            st.markdown("#### 🎯 Final Result:")
                            st.text(str(last_message))
                    except Exception as display_error:
                        st.error(f"Error displaying result: {str(display_error)}")
                        with st.expander("Raw Data", expanded=False):
                            st.json(last_message)
                else:
                    st.info("No results to display.")
        
        with tab2:
            st.markdown("### 💬 Details Processing Steps")
            
            # Display all messages in chronological order
            for i, result in enumerate(st.session_state.analysis_results):
                if "messages" in result and result["messages"]:
                    message = result["messages"][-1]
                    sender = result.get("last_sender", "System")
                    
                    with st.expander(f"Step {i+1}: {sender}", expanded=False):
                        try:
                            if hasattr(message, 'content'):
                                st.markdown(message.content)
                            elif isinstance(message, dict) and "content" in message:
                                st.markdown(message["content"])
                            else:
                                st.text(str(message))
                        except Exception as msg_error:
                            st.error(f"Error displaying message: {str(msg_error)}")
                            with st.expander("Raw Message Data", expanded=False):
                                st.json(message)
        
        with tab3:
            st.markdown("### 📁 Created Files")
            
            # List files in working directory
            if os.path.exists(WORKING_DIRECTORY):
                files = [f for f in os.listdir(WORKING_DIRECTORY) if os.path.isfile(os.path.join(WORKING_DIRECTORY, f))]
                
                if files:
                    for file in files:
                        file_path = os.path.join(WORKING_DIRECTORY, file)
                        file_size = os.path.getsize(file_path)
                        
                        col_file1, col_file2, col_file3 = st.columns([3, 1, 1])
                        
                        with col_file1:
                            st.write(f"📄 {file}")
                        with col_file2:
                            st.write(f"{file_size} bytes")
                        with col_file3:
                            # Download button
                            try:
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        "⬇️ Download",
                                        f.read(),
                                        file_name=file,
                                        key=f"download_{file}"
                                    )
                            except:
                                st.write("N/A")
                else:
                    st.info("No files created.")
        
        with tab4:
            st.markdown("### 📈 Visualizations")
            
            # Look for image files and display them
            if os.path.exists(WORKING_DIRECTORY):
                image_files = [f for f in os.listdir(WORKING_DIRECTORY) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))]
                
                if image_files:
                    for img_file in image_files:
                        img_path = os.path.join(WORKING_DIRECTORY, img_file)
                        st.markdown(f"#### {img_file}")
                        try:
                            st.image(img_path, use_column_width=True)
                        except:
                            st.error(f"Cannot display {img_file}")
                else:
                    st.info("No visualization created.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🤖 <strong>AnalyticsFlow Multi-Agent System</strong> - Powered by LangGraph & Streamlit<br>
        <small>Intelligent multi-agent data analysis system with real-time interaction</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 