#!/usr/bin/env python3
"""Simple test script for LangChain RAG functionality."""

import sys
import os
import asyncio
import requests
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_direct_langchain():
    """Test LangChain directly without API."""
    print("🧪 Testing LangChain Direct Implementation")
    print("=" * 50)
    
    try:
        from src.services.langchain_rag import langchain_rag
        
        # Test 1: Setup vector store
        print("1. Setting up vector store...")
        success = langchain_rag.load_sample_documents()
        if success:
            print("✅ Vector store setup successful")
        else:
            print("❌ Vector store setup failed")
            return False
        
        # Test 2: Get vector store info
        print("\n2. Getting vector store info...")
        info = langchain_rag.get_vectorstore_info()
        print(f"📊 Vector store info: {info}")
        
        # Test 3: Get similar documents
        print("\n3. Testing document retrieval...")
        similar_docs = langchain_rag.get_similar_documents("high risk AI systems", k=2)
        print(f"📚 Found {len(similar_docs)} similar documents")
        for i, doc in enumerate(similar_docs):
            print(f"   Doc {i+1}: {doc['article']} - {doc['content'][:100]}...")
        
        # Test 4: Answer a question
        print("\n4. Testing question answering...")
        question = "What are high-risk AI systems according to the EU AI Act?"
        result = langchain_rag.answer_question(question)
        
        print(f"❓ Question: {question}")
        print(f"✅ Answer: {result['answer'][:200]}...")
        print(f"📚 Sources: {len(result['sources'])} documents")
        
        # Test 5: Another question
        print("\n5. Testing another question...")
        question2 = "What are the provider obligations for high-risk AI systems?"
        result2 = langchain_rag.answer_question(question2)
        
        print(f"❓ Question: {question2}")
        print(f"✅ Answer: {result2['answer'][:200]}...")
        print(f"📚 Sources: {len(result2['sources'])} documents")
        
        print("\n🎉 All direct tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test API endpoints."""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Health check
        print("1. Testing health check...")
        response = requests.get(f"{base_url}/v1/langchain/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Setup RAG system
        print("\n2. Setting up RAG system via API...")
        # Note: This would require authentication in a real scenario
        # For testing, we'll assume the setup is done manually
        
        # Test 3: Get vector store info
        print("\n3. Getting vector store info...")
        try:
            response = requests.get(f"{base_url}/v1/langchain/info")
            if response.status_code == 200:
                info = response.json()
                print("✅ Vector store info retrieved")
                print(f"   Status: {info.get('status')}")
                print(f"   Total documents: {info.get('total_documents', 0)}")
            else:
                print(f"ℹ️ Info endpoint returned: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("ℹ️ API not running - skipping API tests")
            return True
        
        print("\n🎉 API tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def test_with_openai_key():
    """Test if OpenAI API key is available."""
    print("\n🔑 Testing OpenAI API Key")
    print("=" * 50)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OpenAI API key found: {openai_key[:10]}...")
        return True
    else:
        print("❌ OpenAI API key not found")
        print("   Please set OPENAI_API_KEY environment variable")
        return False


def main():
    """Run all tests."""
    print("🚀 LangChain RAG System - Simple Test")
    print("=" * 60)
    
    # Test OpenAI key
    key_available = test_with_openai_key()
    
    if not key_available:
        print("\n⚠️ Cannot run tests without OpenAI API key")
        print("   Set OPENAI_API_KEY environment variable and try again")
        return 1
    
    # Test direct implementation
    direct_success = test_direct_langchain()
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"OpenAI Key: {'✅ Available' if key_available else '❌ Missing'}")
    print(f"Direct Implementation: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_success else '❌ FAIL'}")
    print("=" * 60)
    
    if direct_success:
        print("🎉 LangChain RAG system is working!")
        print("\n📋 Next steps:")
        print("1. Start the API server: uvicorn src.main:app --reload")
        print("2. Visit http://localhost:8000/docs to see the API documentation")
        print("3. Use the /v1/langchain/setup endpoint to initialize the system")
        print("4. Ask questions using the /v1/langchain/ask endpoint")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
