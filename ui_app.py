"""
EU AI Act Compliance RAG System - Streamlit UI

A production-ready Streamlit interface for querying the EU AI Act compliance RAG system.
"""

import streamlit as st
import requests
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="EU AI Act Compliance Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .answer-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .source-item {
        background-color: #e8f4f8;
        border: 1px solid #bee5eb;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .trace-link {
        color: #1f77b4;
        text-decoration: none;
        font-weight: bold;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'api_available' not in st.session_state:
        st.session_state.api_available = None


def check_api_health(api_url: str) -> bool:
    """Check if the API is available."""
    try:
        # Extract base URL from API endpoint
        base_url = api_url.replace('/v1/answer', '')
        health_url = f"{base_url}/health"
        
        response = requests.get(health_url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def query_api(api_url: str, question: str, openai_key: str = None, groq_key: str = None, langsmith_key: str = None, jwt_token: str = None) -> Optional[Dict[str, Any]]:
    """Query the EU AI Act compliance API."""
    try:
        payload = {"question": question}
        
        # Add API keys to payload if provided
        if openai_key:
            payload["openai_key"] = openai_key
        if groq_key:
            payload["groq_key"] = groq_key
        if langsmith_key:
            payload["langsmith_key"] = langsmith_key
            
        headers = {"Content-Type": "application/json"}
        
        # Add JWT token if provided
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("🔐 Authentication required. Please provide a valid JWT token.")
            return None
        elif response.status_code == 403:
            st.error("🚫 Access forbidden. Please check your permissions.")
            return None
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the API. Please ensure the backend is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def display_answer(answer_data: Dict[str, Any]):
    """Display the answer with sources and trace information."""
    # Display answer
    st.markdown("### 📋 Answer")
    st.markdown(f'<div class="answer-box">{answer_data["answer"]}</div>', unsafe_allow_html=True)
    
    # Display sources
    if answer_data.get("sources"):
        st.markdown("### 📚 Sources")
        for i, source in enumerate(answer_data["sources"], 1):
            with st.expander(f"Source {i}: {source.get('filename', 'Unknown')}", expanded=False):
                st.markdown(f"**Content:** {source.get('content', 'No content available')}")
                st.markdown(f"**Source:** {source.get('source', 'Unknown source')}")
                if source.get('compliance_relevance'):
                    st.markdown(f"**Compliance Relevance:** {source['compliance_relevance']}")
                if source.get('risk_implications'):
                    st.markdown(f"**Risk Implications:** {', '.join(source['risk_implications'])}")
                if source.get('similarity_score'):
                    st.markdown(f"**Relevance Score:** {source['similarity_score']:.3f}")
    
    # Display trace URL if available
    if answer_data.get("trace_url"):
        st.markdown("### 🔍 LangSmith Trace")
        st.markdown(f'<a href="{answer_data["trace_url"]}" target="_blank" class="trace-link">View detailed trace in LangSmith →</a>', unsafe_allow_html=True)
    
    # Display compliance metadata if available
    if answer_data.get("compliance_metadata"):
        metadata = answer_data["compliance_metadata"]
        st.markdown("### 📊 Compliance Information")
        col1, col2 = st.columns(2)
        
        with col1:
            if metadata.get("validation"):
                validation = metadata["validation"]
                st.markdown(f"**Compliance Focus:** {'✅ Yes' if validation.get('is_compliance_focused') else '❌ No'}")
                st.markdown(f"**Risk Categories:** {'✅ Yes' if validation.get('mentions_risk_categories') else '❌ No'}")
                st.markdown(f"**Citations:** {'✅ Yes' if validation.get('includes_citations') else '❌ No'}")
        
        with col2:
            st.markdown(f"**Model:** {metadata.get('model', 'Unknown')}")
            st.markdown(f"**Temperature:** {metadata.get('temperature', 'Unknown')}")
            st.markdown(f"**Confidence Score:** {validation.get('confidence_score', 0):.2f}")


def display_query_history():
    """Display query history in sidebar."""
    if st.session_state.query_history:
        st.sidebar.markdown("### 📝 Recent Queries")
        for i, query in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            if st.sidebar.button(f"{i}. {query[:50]}...", key=f"history_{i}"):
                st.session_state.current_question = query


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">⚖️ EU AI Act Compliance Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions about EU AI Act compliance and get expert answers with sources</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.markdown("### ⚙️ Configuration")
    
    # API Keys Configuration
    st.sidebar.markdown("#### 🔑 API Keys")
    st.sidebar.markdown("Configure your API keys to enable the RAG system:")
    
    # OpenAI API Key
    openai_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        help="Your OpenAI API key (starts with sk-proj-)",
        placeholder="sk-proj-..."
    )
    
    # Groq API Key
    groq_key = st.sidebar.text_input(
        "Groq API Key",
        type="password",
        help="Your Groq API key (starts with sk_)",
        placeholder="sk_..."
    )
    
    # LangSmith API Key (optional)
    langsmith_key = st.sidebar.text_input(
        "LangSmith API Key (Optional)",
        type="password",
        help="Your LangSmith API key for tracing (optional)",
        placeholder="ls__..."
    )
    
    # JWT Token (for authenticated requests)
    jwt_token = st.sidebar.text_input(
        "JWT Token (Optional)",
        type="password",
        help="JWT token for authenticated requests",
        placeholder="eyJ..."
    )
    
    # Store API keys in session state
    if openai_key:
        st.session_state.openai_key = openai_key
    if groq_key:
        st.session_state.groq_key = groq_key
    if langsmith_key:
        st.session_state.langsmith_key = langsmith_key
    if jwt_token:
        st.session_state.jwt_token = jwt_token
    
    # Display API keys status
    st.sidebar.markdown("#### 📊 Status")
    if st.session_state.get('openai_key'):
        st.sidebar.success("✅ OpenAI Key: Configured")
    else:
        st.sidebar.warning("⚠️ OpenAI Key: Not configured")
    
    if st.session_state.get('groq_key'):
        st.sidebar.success("✅ Groq Key: Configured")
    else:
        st.sidebar.info("ℹ️ Groq Key: Optional")
    
    if st.session_state.get('langsmith_key'):
        st.sidebar.success("✅ LangSmith Key: Configured")
    else:
        st.sidebar.info("ℹ️ LangSmith Key: Optional")
    
    if st.session_state.get('jwt_token'):
        st.sidebar.success("✅ JWT Token: Configured")
    else:
        st.sidebar.info("ℹ️ JWT Token: Optional")
    
    st.sidebar.markdown("---")
    
    # API URL configuration
    st.sidebar.markdown("#### 🌐 API Configuration")
    default_api_url = os.getenv("API_URL", "http://localhost:8000/v1/answer")
    api_url = st.sidebar.text_input(
        "API Endpoint URL",
        value=default_api_url,
        help="URL of the EU AI Act compliance API endpoint"
    )
    
    # API health check
    if st.sidebar.button("🔍 Check API Health"):
        with st.sidebar.spinner("Checking API..."):
            is_healthy = check_api_health(api_url)
            if is_healthy:
                st.sidebar.success("✅ API is available")
                st.session_state.api_available = True
            else:
                st.sidebar.error("❌ API is not available")
                st.session_state.api_available = False
    
    # API Keys Instructions
    st.sidebar.markdown("### 📖 How to Get API Keys")
    
    with st.sidebar.expander("🔑 OpenAI API Key", expanded=False):
        st.markdown("""
        1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
        2. Sign in to your account
        3. Click "Create new secret key"
        4. Copy the key (starts with `sk-proj-`)
        5. Paste it in the field above
        """)
    
    with st.sidebar.expander("🤖 Groq API Key", expanded=False):
        st.markdown("""
        1. Go to [Groq Console](https://console.groq.com/keys)
        2. Sign in to your account
        3. Click "Create API Key"
        4. Copy the key (starts with `sk_`)
        5. Paste it in the field above
        """)
    
    with st.sidebar.expander("🔍 LangSmith API Key", expanded=False):
        st.markdown("""
        1. Go to [LangSmith](https://smith.langchain.com/)
        2. Sign in to your account
        3. Go to Settings > API Keys
        4. Copy the key (starts with `ls__`)
        5. Paste it in the field above
        """)
    
    with st.sidebar.expander("🔐 JWT Token", expanded=False):
        st.markdown("""
        1. Start the backend API
        2. Go to http://localhost:8000/docs
        3. Use the `/v1/auth/login` endpoint
        4. Login with: `analyst` / `analyst`
        5. Copy the `access_token` from response
        """)
    
    # Backend instructions
    st.sidebar.markdown("### 🚀 Backend Instructions")
    st.sidebar.markdown("""
    To start the backend:
    ```bash
    uvicorn src.main:app --reload
    ```
    
    Or use Docker:
    ```bash
    make docker-build
    make docker-run
    ```
    """)
    
    # Display query history
    display_query_history()
    
    # Main query interface
    st.markdown("### 💬 Ask a Compliance Question")
    
    # Question input
    default_question = "What qualifies a system as high-risk under the EU AI Act?"
    question = st.text_area(
        "Enter your EU AI Act compliance question:",
        value=default_question,
        height=100,
        help="Ask specific questions about EU AI Act compliance, requirements, or obligations"
    )
    
    # Query button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ask_button = st.button("🔍 Ask Question", type="primary", use_container_width=True)
    
    # Process query
    if ask_button and question.strip():
        # Add to query history
        if question not in st.session_state.query_history:
            st.session_state.query_history.append(question)
        
        # Show loading spinner
        with st.spinner("🔍 Analyzing your question with EU AI Act compliance expertise..."):
            # Query the API with user-provided keys
            answer_data = query_api(
                api_url, 
                question,
                openai_key=st.session_state.get('openai_key'),
                groq_key=st.session_state.get('groq_key'),
                langsmith_key=st.session_state.get('langsmith_key'),
                jwt_token=st.session_state.get('jwt_token')
            )
        
        if answer_data:
            # Display success message
            st.markdown('<div class="success-box">✅ Successfully retrieved compliance information</div>', unsafe_allow_html=True)
            
            # Display the answer
            display_answer(answer_data)
            
            # Add timestamp
            st.markdown(f"*Query processed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        else:
            st.markdown('<div class="error-box">❌ Failed to retrieve answer. Please check your API connection and try again.</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>EU AI Act Compliance Assistant | Powered by LangSmith & FastAPI</p>
        <p>For technical support, check the backend logs and ensure all services are running.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
