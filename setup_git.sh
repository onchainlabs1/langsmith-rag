#!/bin/bash

# Script to configure and upload the langsmith-rag project to GitHub
# Repository: https://github.com/onchainlabs1/langsmith-rag

echo "🚀 Configuring langsmith-rag project for GitHub..."
echo "Repository: https://github.com/onchainlabs1/langsmith-rag"
echo "================================================"

# Check if we're in the correct directory
if [ ! -f "src/main.py" ]; then
    echo "❌ Error: Run this script from the langsmith-rag project root"
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Install Git first."
    exit 1
fi

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
fi

# Add remote if it doesn't exist
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Adding remote origin..."
    git remote add origin https://github.com/onchainlabs1/langsmith-rag.git
fi

# Check status
echo "📊 Current git status:"
git status

# Add all files
echo "📝 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️ No changes to commit."
else
    # Make commit
    echo "💾 Making initial commit..."
    git commit -m "🚀 Initial commit: EU AI Act Compliance RAG System

- ✅ Groq + LangChain implementation
- ✅ LangSmith tracing integration  
- ✅ FastAPI with JWT authentication
- ✅ Streamlit UI interface
- ✅ Comprehensive testing suite
- ✅ Docker support
- ✅ Monitoring with Prometheus/Grafana
- ✅ Complete documentation
- ✅ Auto-detection: Groq > OpenAI > Mock
- ✅ Ultra-fast inference (~300 tokens/sec)
- ✅ Cost-effective (10x cheaper than OpenAI)
- ✅ EU-friendly (no data leaving EU)"

    # Push to GitHub
    echo "⬆️ Pushing to GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ Success! Project uploaded to GitHub."
        echo "🔗 Access: https://github.com/onchainlabs1/langsmith-rag"
    else
        echo "❌ Error uploading to GitHub. Check your connection and credentials."
        exit 1
    fi
fi

echo ""
echo "🎉 Configuration completed!"
echo "📋 Next steps:"
echo "1. Configure your API keys:"
echo "   export GROQ_API_KEY='your_groq_key'"
echo "   export LANGCHAIN_API_KEY='your_langsmith_api_key_here'"
echo "   export OPENAI_API_KEY='your_openai_key'"
echo ""
echo "2. Test the system:"
echo "   python3 test_groq_langchain.py"
echo ""
echo "3. Start the server:"
echo "   uvicorn src.main:app --reload"
echo ""
echo "4. Access the documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "🔗 Repository: https://github.com/onchainlabs1/langsmith-rag"
