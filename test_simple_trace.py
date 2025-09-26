#!/usr/bin/env python3
"""
Simple test using LangChain Tracer
"""

import os
from langchain_core.tracers import LangChainTracer
from langsmith import Client

def test_langchain_tracer():
    """Test using LangChain Tracer."""
    print("🧪 Testing LangChain Tracer...")
    
    try:
        # Create client and tracer
        client = Client(api_key=os.getenv('LANGSMITH_API_KEY'))
        tracer = LangChainTracer(
            project_name=os.getenv('LANGSMITH_PROJECT', 'default'),
            client=client
        )
        
        print("✅ LangChain Tracer created successfully!")
        print(f"📁 Project: {os.getenv('LANGSMITH_PROJECT', 'default')}")
        
        # Test creating a simple run
        run_id = tracer.create_run(
            name="test_run",
            run_type="chain",
            inputs={"test": "Hello from LangChain Tracer"},
            tags=["test", "langchain-tracer"]
        )
        
        print(f"✅ Run created: {run_id}")
        
        # Update with outputs
        tracer.update_run(
            run_id=run_id,
            outputs={"result": "Test completed successfully"}
        )
        
        print(f"✅ Run updated with outputs")
        print(f"🔗 Trace URL: https://smith.langchain.com/trace/{run_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_langchain_tracer()
