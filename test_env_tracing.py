#!/usr/bin/env python3
"""
Test tracing via environment variables
"""

import os
from langchain_core.tracers import LangChainTracer
from langsmith import Client

def test_env_tracing():
    """Test tracing via environment variables."""
    print("🧪 Testing Environment Variable Tracing...")
    
    # Set environment variables for automatic tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv('LANGSMITH_PROJECT', 'default')
    
    print(f"✅ Environment variables set:")
    print(f"  LANGCHAIN_TRACING_V2: {os.environ.get('LANGCHAIN_TRACING_V2')}")
    print(f"  LANGCHAIN_PROJECT: {os.environ.get('LANGCHAIN_PROJECT')}")
    print(f"  LANGCHAIN_API_KEY: {'Set' if os.getenv('LANGCHAIN_API_KEY') else 'Not set'}")
    
    try:
        # Create a simple LangChain run that should be traced automatically
        from langchain_core.runnables import RunnableLambda
        
        def simple_function(inputs):
            return {"result": f"Processed: {inputs['text']}"}
        
        # Create a runnable
        runnable = RunnableLambda(simple_function)
        
        # This should create a trace automatically
        result = runnable.invoke({"text": "Hello LangSmith!"})
        
        print(f"✅ Runnable executed: {result}")
        print(f"🎯 Check LangSmith dashboard for traces!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_env_tracing()
