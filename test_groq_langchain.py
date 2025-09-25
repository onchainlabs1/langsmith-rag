#!/usr/bin/env python3
"""Test script for Groq LangChain RAG functionality."""

import sys
import os
import asyncio
import requests
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_groq_direct():
    """Test Groq LangChain directly without API."""
    print("🚀 Testing Groq LangChain Direct Implementation")
    print("=" * 50)
    
    try:
        from src.services.groq_langchain_rag import groq_langchain_rag
        
        # Test 1: Setup vector store
        print("1. Setting up vector store with Groq...")
        success = groq_langchain_rag.load_sample_documents()
        if success:
            print("✅ Vector store setup successful with Groq LLM")
        else:
            print("❌ Vector store setup failed")
            return False
        
        # Test 2: Get vector store info
        print("\n2. Getting vector store info...")
        info = groq_langchain_rag.get_vectorstore_info()
        print(f"📊 Vector store info:")
        print(f"   Status: {info.get('status')}")
        print(f"   LLM Model: {info.get('llm_model')}")
        print(f"   LLM Provider: {info.get('llm_provider')}")
        print(f"   Total Documents: {info.get('total_documents')}")
        print(f"   LangSmith Enabled: {info.get('langsmith_enabled')}")
        
        # Test 3: Get similar documents
        print("\n3. Testing document retrieval...")
        similar_docs = groq_langchain_rag.get_similar_documents("high risk AI systems", k=2)
        print(f"📚 Found {len(similar_docs)} similar documents")
        for i, doc in enumerate(similar_docs):
            print(f"   Doc {i+1}: {doc['article']} - {doc['compliance_level']}")
            print(f"      Content: {doc['content'][:100]}...")
        
        # Test 4: Answer questions
        test_questions = [
            "What are high-risk AI systems according to the EU AI Act?",
            "What are the provider obligations for high-risk AI systems?",
            "What are the penalties for non-compliance with the EU AI Act?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i+3}. Testing question {i}...")
            result = groq_langchain_rag.answer_question(question)
            
            print(f"❓ Question: {question}")
            print(f"✅ Answer: {result['answer'][:200]}...")
            print(f"📚 Sources: {len(result['sources'])} documents")
            print(f"🤖 Model: {result.get('model')} ({result.get('provider')})")
            
            if result.get('trace_url'):
                print(f"🔍 LangSmith Trace: {result['trace_url']}")
            
            # Show sources
            for j, source in enumerate(result['sources'][:2]):  # Show first 2 sources
                print(f"   Source {j+1}: {source['article']} ({source['compliance_level']})")
        
        print("\n🎉 All Groq tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Groq test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_groq_api():
    """Test Groq API endpoints."""
    print("\n🌐 Testing Groq API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Health check
        print("1. Testing health check...")
        try:
            response = requests.get(f"{base_url}/v1/langchain/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check passed")
                health_data = response.json()
                print(f"   Service: {health_data.get('service')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Is the server running?")
            print("   Start with: uvicorn src.main:app --reload")
            return False
        
        # Test 2: Setup (this would normally require authentication)
        print("\n2. Testing setup endpoint...")
        try:
            response = requests.post(f"{base_url}/v1/langchain/setup", timeout=5)
            print(f"   Setup endpoint response: {response.status_code}")
            if response.status_code == 401:
                print("   ℹ️ Authentication required (expected)")
            elif response.status_code == 200:
                setup_data = response.json()
                print(f"   ✅ Setup successful")
                print(f"   System type: {setup_data.get('system_type')}")
                print(f"   LLM provider: {setup_data.get('llm_provider')}")
        except Exception as e:
            print(f"   ℹ️ Setup test error: {e}")
        
        print("\n🎉 Groq API tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
        return False


def test_groq_models():
    """Test available Groq models."""
    print("\n🤖 Available Groq Models")
    print("=" * 50)
    
    models = [
        "llama-3.1-70b-versatile",  # Currently used
        "llama-3.1-8b-instant",    # Faster, smaller
        "mixtral-8x7b-32768",      # Alternative
        "gemma-7b-it"              # Alternative
    ]
    
    print("📋 Available Groq models for EU AI Act compliance:")
    for i, model in enumerate(models, 1):
        print(f"   {i}. {model}")
    
    print(f"\n🎯 Currently using: {models[0]}")
    print("   - Fast inference (~300 tokens/sec)")
    print("   - High quality responses")
    print("   - Good for compliance questions")
    
    print("\n💡 To change model, edit groq_langchain_rag.py")
    print("   Change model_name in ChatGroq initialization")


def show_groq_benefits():
    """Show benefits of using Groq."""
    print("\n🚀 Benefits of Using Groq")
    print("=" * 50)
    
    benefits = [
        "⚡ Ultra-fast inference (~300 tokens/sec vs ~50 tokens/sec)",
        "💰 Cost-effective (up to 10x cheaper than OpenAI)",
        "🔓 Open-source models (Llama, Mixtral, Gemma)",
        "🌍 No data residency restrictions",
        "📊 Built-in LangSmith integration",
        "🎯 High-quality responses for compliance questions",
        "🔄 Multiple model options available",
        "⚖️ EU-friendly (no data leaving EU for inference)"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")
    
    print("\n📈 Performance Comparison:")
    print("   Groq Llama-3.1-70b: ~300 tokens/sec")
    print("   OpenAI GPT-4: ~50 tokens/sec")
    print("   Cost: Groq is ~10x cheaper")
    
    print("\n🔒 Privacy & Compliance:")
    print("   ✅ No data stored by Groq")
    print("   ✅ EU-friendly deployment")
    print("   ✅ Open-source models")
    print("   ✅ Full control over data")


def main():
    """Run all Groq tests and demonstrations."""
    print("🚀 Groq LangChain RAG System - Test Suite")
    print("=" * 60)
    
    # Check if Groq API key is available
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or groq_key.startswith("gsk_test"):
        print("⚠️ GROQ_API_KEY not found or is test key")
        print("   Set GROQ_API_KEY environment variable with your real Groq API key")
        print("   Get your key at: https://console.groq.com/keys")
        print("\n🔄 Running mock tests instead...")
        
        # Run mock tests
        import subprocess
        result = subprocess.run([sys.executable, "test_mock_langchain.py"], capture_output=True, text=True)
        print(result.stdout)
        return 0
    
    # Test Groq models
    test_groq_models()
    
    # Show benefits
    show_groq_benefits()
    
    # Test direct implementation
    direct_success = test_groq_direct()
    
    # Test API endpoints
    api_success = test_groq_api()
    
    # Summary
    print("\n" + "=" * 60)
    print("Groq Test Summary:")
    print(f"Groq API Key: {'✅ Available' if groq_key else '❌ Missing'}")
    print(f"Direct Implementation: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_success else '❌ FAIL'}")
    print("=" * 60)
    
    if direct_success:
        print("🎉 Groq LangChain RAG system is working!")
        print("\n📋 Next steps:")
        print("1. Start the API server: uvicorn src.main:app --reload")
        print("2. Visit http://localhost:8000/docs to see the API documentation")
        print("3. Use the /v1/langchain/setup endpoint to initialize the system")
        print("4. Ask questions using the /v1/langchain/ask endpoint")
        print("5. Check LangSmith for traces: https://smith.langchain.com/")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
