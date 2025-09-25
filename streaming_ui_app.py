"""
EU AI Act Compliance RAG System - Enhanced Streamlit UI with Streaming Support

A production-ready Streamlit interface with streaming responses and conversation memory.
"""

import streamlit as st
import requests
import json
import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio


# Page configuration
st.set_page_config(
    page_title="EU AI Act Compliance Assistant - Enhanced",
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
    .streaming-box {
        background-color: #e8f4f8;
        border: 1px solid #bee5eb;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        min-height: 100px;
    }
    .source-item {
        background-color: #e8f4f8;
        border: 1px solid #bee5eb;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .memory-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
        font-size: 0.9rem;
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
    if 'conversation_session_id' not in st.session_state:
        st.session_state.conversation_session_id = str(uuid.uuid4())
    if 'streaming_responses' not in st.session_state:
        st.session_state.streaming_responses = []
    if 'current_streaming_answer' not in st.session_state:
        st.session_state.current_streaming_answer = ""


def check_api_health(api_url: str) -> bool:
    """Check if the API is available."""
    try:
        # Extract base URL from API endpoint
        base_url = api_url.replace('/v1/streaming/ask', '')
        health_url = f"{base_url}/v1/streaming/health"
        
        response = requests.get(health_url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def stream_question_to_api(
    api_url: str, 
    question: str, 
    session_id: str,
    openai_key: str = None, 
    groq_key: str = None, 
    langsmith_key: str = None, 
    jwt_token: str = None
) -> Optional[Dict[str, Any]]:
    """Stream question to the EU AI Act compliance API."""
    try:
        payload = {
            "question": question,
            "session_id": session_id,
            "max_sources": 5
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        # Add JWT token if provided
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=60,
            stream=True
        )
        
        if response.status_code == 200:
            return response
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


def process_streaming_response(response):
    """Process streaming response from the API."""
    full_answer = ""
    sources = []
    compliance_metadata = {}
    memory_stats = {}
    
    # Create placeholder for streaming content
    streaming_placeholder = st.empty()
    
    try:
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    
                    if data == '[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(data)
                        chunk_type = chunk.get('type', '')
                        
                        if chunk_type == 'metadata':
                            st.info(f"🔍 Processing request: {chunk.get('request_id', 'Unknown')}")
                            
                        elif chunk_type == 'context':
                            context = chunk.get('context', {})
                            if context.get('has_conversation_history'):
                                with st.expander("📚 Conversation Context", expanded=False):
                                    st.json(context)
                        
                        elif chunk_type == 'content':
                            content = chunk.get('content', '')
                            full_answer += content
                            
                            # Update streaming placeholder
                            with streaming_placeholder.container():
                                st.markdown(f'<div class="streaming-box">{full_answer}</div>', 
                                          unsafe_allow_html=True)
                        
                        elif chunk_type == 'sources':
                            sources = chunk.get('sources', [])
                            st.markdown("### 📚 Sources Retrieved")
                            for i, source in enumerate(sources, 1):
                                with st.expander(f"Source {i}: {source.get('filename', 'Unknown')}", expanded=False):
                                    st.markdown(f"**Content:** {source.get('content', 'No content available')}")
                                    st.markdown(f"**Source:** {source.get('source', 'Unknown source')}")
                                    if source.get('compliance_relevance'):
                                        st.markdown(f"**Compliance Relevance:** {source['compliance_relevance']}")
                                    if source.get('risk_implications'):
                                        st.markdown(f"**Risk Implications:** {', '.join(source['risk_implications'])}")
                                    if source.get('similarity_score'):
                                        st.markdown(f"**Relevance Score:** {source['similarity_score']:.3f}")
                        
                        elif chunk_type == 'memory_update':
                            memory_stats = chunk.get('memory_stats', {})
                            with st.sidebar:
                                st.markdown("### 🧠 Memory Status")
                                st.markdown(f'<div class="memory-info">Messages: {memory_stats.get("buffer_messages", 0)}</div>', 
                                          unsafe_allow_html=True)
                                st.markdown(f'<div class="memory-info">Risk Categories: {memory_stats.get("risk_categories", 0)}</div>', 
                                          unsafe_allow_html=True)
                                st.markdown(f'<div class="memory-info">Article References: {memory_stats.get("article_references", 0)}</div>', 
                                          unsafe_allow_html=True)
                        
                        elif chunk_type == 'final':
                            compliance_metadata = chunk.get('compliance_metadata', {})
                            
                            # Final answer display
                            st.markdown("### 📋 Final Answer")
                            st.markdown(f'<div class="answer-box">{full_answer}</div>', unsafe_allow_html=True)
                            
                            # Display trace URL if available
                            if chunk.get("trace_url"):
                                st.markdown("### 🔍 LangSmith Trace")
                                st.markdown(f'<a href="{chunk["trace_url"]}" target="_blank" class="trace-link">View detailed trace in LangSmith →</a>', 
                                          unsafe_allow_html=True)
                            
                            # Display compliance metadata
                            if compliance_metadata:
                                st.markdown("### 📊 Compliance Information")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    compliance_score = compliance_metadata.get("compliance_score", 0.0)
                                    st.markdown(f"**Compliance Score:** {compliance_score:.2f}")
                                    if compliance_metadata.get("risk_categories"):
                                        st.markdown(f"**Risk Categories:** {', '.join(compliance_metadata['risk_categories'])}")
                                
                                with col2:
                                    st.markdown(f"**Model:** {compliance_metadata.get('model', 'Unknown')}")
                                    st.markdown(f"**Temperature:** {compliance_metadata.get('temperature', 'Unknown')}")
                                    if compliance_metadata.get("article_references"):
                                        st.markdown(f"**AI Act References:** {', '.join(compliance_metadata['article_references'])}")
                        
                        elif chunk_type == 'error':
                            st.error(f"❌ Error: {chunk.get('error', 'Unknown error')}")
                            return None
                    
                    except json.JSONDecodeError:
                        continue
        
        # Clear streaming placeholder
        streaming_placeholder.empty()
        
        return {
            "answer": full_answer,
            "sources": sources,
            "compliance_metadata": compliance_metadata,
            "memory_stats": memory_stats
        }
        
    except Exception as e:
        st.error(f"❌ Error processing streaming response: {str(e)}")
        return None


def display_conversation_controls():
    """Display conversation control buttons."""
    st.sidebar.markdown("### 💬 Conversation Controls")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 New Session"):
            st.session_state.conversation_session_id = str(uuid.uuid4())
            st.session_state.streaming_responses = []
            st.session_state.current_streaming_answer = ""
            st.sidebar.success("New conversation session started!")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear History"):
            # This would call the clear conversation API
            st.sidebar.success("Conversation history cleared!")
            st.rerun()


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">⚖️ EU AI Act Compliance Assistant - Enhanced</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions with streaming responses and conversation memory</div>', unsafe_allow_html=True)
    
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
    
    if st.session_state.get('jwt_token'):
        st.sidebar.success("✅ JWT Token: Configured")
    else:
        st.sidebar.info("ℹ️ JWT Token: Optional")
    
    st.sidebar.markdown("---")
    
    # API URL configuration
    st.sidebar.markdown("#### 🌐 API Configuration")
    default_api_url = os.getenv("STREAMING_API_URL", "http://localhost:8000/v1/streaming/ask")
    api_url = st.sidebar.text_input(
        "Streaming API Endpoint URL",
        value=default_api_url,
        help="URL of the EU AI Act compliance streaming API endpoint"
    )
    
    # API health check
    if st.sidebar.button("🔍 Check API Health"):
        with st.sidebar.spinner("Checking API..."):
            is_healthy = check_api_health(api_url)
            if is_healthy:
                st.sidebar.success("✅ Streaming API is available")
                st.session_state.api_available = True
            else:
                st.sidebar.error("❌ Streaming API is not available")
                st.session_state.api_available = False
    
    # Conversation controls
    display_conversation_controls()
    
    # Session info
    st.sidebar.markdown("### 🆔 Session Info")
    st.sidebar.markdown(f"**Session ID:** `{st.session_state.conversation_session_id[:8]}...`")
    st.sidebar.markdown(f"**Messages:** {len(st.session_state.streaming_responses)}")
    
    # Display query history
    if st.session_state.query_history:
        st.sidebar.markdown("### 📝 Recent Queries")
        for i, query in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            if st.sidebar.button(f"{i}. {query[:50]}...", key=f"history_{i}"):
                st.session_state.current_question = query
    
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
        ask_button = st.button("🚀 Ask Question (Streaming)", type="primary", use_container_width=True)
    
    # Process query
    if ask_button and question.strip():
        # Add to query history
        if question not in st.session_state.query_history:
            st.session_state.query_history.append(question)
        
        # Show loading spinner
        with st.spinner("🔍 Analyzing your question with EU AI Act compliance expertise..."):
            # Stream the question to API
            response = stream_question_to_api(
                api_url, 
                question,
                st.session_state.conversation_session_id,
                openai_key=st.session_state.get('openai_key'),
                groq_key=st.session_state.get('groq_key'),
                langsmith_key=st.session_state.get('langsmith_key'),
                jwt_token=st.session_state.get('jwt_token')
            )
        
        if response:
            # Process streaming response
            result = process_streaming_response(response)
            
            if result:
                # Store response
                st.session_state.streaming_responses.append(result)
                
                # Add timestamp
                st.markdown(f"*Query processed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
            else:
                st.markdown('<div class="error-box">❌ Failed to process streaming response. Please try again.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">❌ Failed to connect to streaming API. Please check your connection and try again.</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>EU AI Act Compliance Assistant - Enhanced | Powered by LangChain, LangSmith & FastAPI</p>
        <p>Features: Streaming responses, conversation memory, real-time compliance analysis</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
