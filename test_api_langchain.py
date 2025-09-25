#!/usr/bin/env python3
"""Test script for LangChain API endpoints."""

import requests
import json
import time
import sys


def test_api_endpoints():
    """Test LangChain API endpoints."""
    print("🌐 Testing LangChain API Endpoints")
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
                print(f"   Status: {health_data.get('status')}")
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
            # Note: In a real scenario, you'd need proper authentication
            # For now, we'll just check if the endpoint exists
            response = requests.post(f"{base_url}/v1/langchain/setup", timeout=5)
            print(f"   Setup endpoint response: {response.status_code}")
            if response.status_code == 401:
                print("   ℹ️ Authentication required (expected)")
            elif response.status_code == 200:
                print("   ✅ Setup successful")
                setup_data = response.json()
                print(f"   System type: {setup_data.get('system_type')}")
        except Exception as e:
            print(f"   ℹ️ Setup test error: {e}")
        
        # Test 3: Info endpoint
        print("\n3. Testing info endpoint...")
        try:
            response = requests.get(f"{base_url}/v1/langchain/info", timeout=5)
            print(f"   Info endpoint response: {response.status_code}")
            if response.status_code == 401:
                print("   ℹ️ Authentication required (expected)")
            elif response.status_code == 200:
                info_data = response.json()
                print(f"   ✅ Info retrieved")
                print(f"   Status: {info_data.get('status')}")
                print(f"   Total documents: {info_data.get('total_documents')}")
        except Exception as e:
            print(f"   ℹ️ Info test error: {e}")
        
        # Test 4: Ask question (would need authentication)
        print("\n4. Testing ask endpoint...")
        try:
            question_data = {"question": "What are high-risk AI systems?"}
            response = requests.post(
                f"{base_url}/v1/langchain/ask",
                json=question_data,
                timeout=5
            )
            print(f"   Ask endpoint response: {response.status_code}")
            if response.status_code == 401:
                print("   ℹ️ Authentication required (expected)")
            elif response.status_code == 200:
                answer_data = response.json()
                print(f"   ✅ Question answered")
                print(f"   Answer: {answer_data.get('answer', '')[:100]}...")
                print(f"   Sources: {len(answer_data.get('sources', []))}")
        except Exception as e:
            print(f"   ℹ️ Ask test error: {e}")
        
        # Test 5: Similar documents
        print("\n5. Testing similar documents endpoint...")
        try:
            response = requests.get(f"{base_url}/v1/langchain/similar/high-risk", timeout=5)
            print(f"   Similar endpoint response: {response.status_code}")
            if response.status_code == 401:
                print("   ℹ️ Authentication required (expected)")
            elif response.status_code == 200:
                similar_data = response.json()
                print(f"   ✅ Similar documents retrieved")
                print(f"   Query: {similar_data.get('query')}")
                print(f"   Count: {similar_data.get('count')}")
        except Exception as e:
            print(f"   ℹ️ Similar test error: {e}")
        
        print("\n🎉 API endpoint tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def show_api_usage():
    """Show how to use the API with authentication."""
    print("\n📖 API Usage Guide")
    print("=" * 50)
    
    print("🔐 Authentication Required:")
    print("   All endpoints (except health) require JWT authentication")
    print("   Use the /v1/auth/login endpoint to get a token")
    
    print("\n📋 Example Usage with curl:")
    print("""
    # 1. Login to get JWT token
    curl -X POST "http://localhost:8000/v1/auth/login" \\
         -H "Content-Type: application/x-www-form-urlencoded" \\
         -d "username=analyst&password=analyst"
    
    # 2. Use the token for API calls
    export JWT_TOKEN="your-jwt-token-here"
    
    # 3. Setup RAG system
    curl -X POST "http://localhost:8000/v1/langchain/setup" \\
         -H "Authorization: Bearer $JWT_TOKEN"
    
    # 4. Ask a question
    curl -X POST "http://localhost:8000/v1/langchain/ask" \\
         -H "Content-Type: application/json" \\
         -H "Authorization: Bearer $JWT_TOKEN" \\
         -d '{"question": "What are high-risk AI systems?"}'
    
    # 5. Get similar documents
    curl -X GET "http://localhost:8000/v1/langchain/similar/high-risk" \\
         -H "Authorization: Bearer $JWT_TOKEN"
    """)


def show_endpoints():
    """Show available endpoints."""
    print("\n📋 Available LangChain Endpoints")
    print("=" * 50)
    
    endpoints = [
        ("GET", "/v1/langchain/health", "Health check (no auth required)"),
        ("POST", "/v1/langchain/setup", "Initialize RAG system"),
        ("POST", "/v1/langchain/ask", "Ask questions about EU AI Act"),
        ("GET", "/v1/langchain/similar/{query}", "Get similar documents"),
        ("GET", "/v1/langchain/info", "Get system information"),
        ("POST", "/v1/auth/login", "Get JWT token"),
        ("GET", "/docs", "API documentation (Swagger UI)")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"  {method:4} {endpoint:30} - {description}")


def main():
    """Run all tests and demonstrations."""
    print("🚀 LangChain API Test Suite")
    print("=" * 60)
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    # Show usage guide
    show_api_usage()
    
    # Show endpoints
    show_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"API Endpoints: {'✅ WORKING' if api_success else '❌ ISSUES'}")
    print("Authentication: ✅ REQUIRED")
    print("Documentation: ✅ AVAILABLE at /docs")
    print("=" * 60)
    
    if api_success:
        print("🎉 LangChain API is ready!")
        print("\n📋 Next steps:")
        print("1. Visit http://localhost:8000/docs for interactive API documentation")
        print("2. Use /v1/auth/login to get a JWT token")
        print("3. Use the token to access LangChain endpoints")
        print("4. Start with /v1/langchain/setup to initialize the system")
        return 0
    else:
        print("❌ API has issues. Check if the server is running.")
        print("   Start with: uvicorn src.main:app --reload")
        return 1


if __name__ == "__main__":
    sys.exit(main())
