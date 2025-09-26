#!/bin/bash

# LangSmith Tracing Setup Script
echo "🚀 Setting up LangSmith Tracing..."

# Set LangSmith environment variables
export LANGSMITH_API_KEY="your_langsmith_api_key_here"
export LANGSMITH_PROJECT="default"
export LANGCHAIN_API_KEY="your_langchain_api_key_here"
export LANGCHAIN_PROJECT="default"
export LANGCHAIN_TRACING_V2=true
export LANGSMITH_TRACING=true
export LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Set API keys (use placeholder for testing)
export GROQ_API_KEY="gsk_test_key_placeholder"
export OPENAI_API_KEY="sk-test_key_placeholder"

echo "✅ Environment variables configured:"
echo "  LANGSMITH_API_KEY: ${LANGSMITH_API_KEY:0:20}..."
echo "  LANGSMITH_PROJECT: $LANGSMITH_PROJECT"
echo "  LANGCHAIN_API_KEY: ${LANGCHAIN_API_KEY:0:20}..."
echo "  LANGCHAIN_PROJECT: $LANGCHAIN_PROJECT"
echo "  LANGCHAIN_TRACING_V2: $LANGCHAIN_TRACING_V2"

echo ""
echo "🎯 Tracing is now enabled!"
echo "📊 Check LangSmith dashboard: https://smith.langchain.com"
echo "📁 Project: $LANGSMITH_PROJECT"
echo ""
echo "🚀 You can now run:"
echo "  python3 test_env_tracing.py"
echo "  uvicorn src.main:app --reload"
echo "  streamlit run streaming_ui_app.py"
