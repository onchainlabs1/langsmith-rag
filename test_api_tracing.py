#!/usr/bin/env python3
"""
Test API tracing directly
"""

import os
import requests
import time

def test_api_tracing():
    """Test API tracing."""
    print("🧪 Testing API Tracing...")
    
    # Set environment variables
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "default"
    os.environ["LANGCHAIN_API_KEY"] = "your_langchain_api_key_here"
    
    print("✅ Environment variables set")
    
    try:
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        health_response = requests.get("http://localhost:8000/health")
        print(f"✅ Health check: {health_response.status_code}")
        
        # Test setup endpoint
        print("🔍 Testing setup endpoint...")
        setup_response = requests.get("http://localhost:8000/v1/langchain/setup")
        print(f"✅ Setup check: {setup_response.status_code}")
        
        if setup_response.status_code == 200:
            setup_data = setup_response.json()
            print(f"📊 Setup data: {setup_data}")
        
        # Test ask endpoint with a simple question
        print("🔍 Testing ask endpoint...")
        ask_data = {
            "question": "What are high-risk AI systems under the EU AI Act?"
        }
        
        ask_response = requests.post(
            "http://localhost:8000/v1/langchain/ask",
            json=ask_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Ask endpoint: {ask_response.status_code}")
        
        if ask_response.status_code == 200:
            response_data = ask_response.json()
            print(f"📝 Response: {response_data.get('answer', 'No answer')[:100]}...")
            print(f"🔗 Trace URL: {response_data.get('trace_url', 'No trace URL')}")
        else:
            print(f"❌ Error response: {ask_response.text}")
        
        print("🎯 Check LangSmith dashboard for traces!")
        print("📊 Dashboard: https://smith.langchain.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_tracing()
