#!/usr/bin/env python3
"""
Simple test to verify LangSmith tracing is working
"""

import os
from langsmith import Client
from langchain_core.tracers import LangChainTracer

def test_simple_trace():
    """Test simple trace creation."""
    print("🔍 Testing Simple LangSmith Trace...")
    
    # Check environment variables
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
    langsmith_project = os.getenv("LANGSMITH_PROJECT", "pr-juicy-improvement-41")
    
    print(f"📋 Configuration:")
    print(f"  LANGSMITH_API_KEY: {'✅ Set' if langsmith_api_key else '❌ Not set'}")
    print(f"  LANGSMITH_PROJECT: {langsmith_project}")
    
    if not langsmith_api_key:
        print("❌ Error: LANGSMITH_API_KEY not found!")
        return False
    
    try:
        # Create LangSmith client
        client = Client(api_key=langsmith_api_key)
        
        # Create a simple trace
        with client.trace(
            name="test_trace",
            run_type="chain",
            inputs={"test": "Hello LangSmith"},
            project_name=langsmith_project,
            tags=["test", "simple"],
            metadata={"source": "test_script"}
        ) as trace:
            # Simulate some work
            result = "Test completed successfully"
            trace.outputs = {"result": result}
            
        print(f"✅ Trace created successfully!")
        print(f"🔗 Trace ID: {trace.id}")
        print(f"🌐 Trace URL: https://smith.langchain.com/trace/{trace.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating trace: {str(e)}")
        return False

if __name__ == "__main__":
    test_simple_trace()
