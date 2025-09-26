#!/usr/bin/env python3
"""
Direct trace test using LangSmith client
"""

import os
from langsmith import Client

def test_direct_trace():
    """Test direct trace creation."""
    print("🧪 Testing Direct LangSmith Trace...")
    
    try:
        # Create client
        client = Client(api_key=os.getenv('LANGSMITH_API_KEY'))
        project_name = os.getenv('LANGSMITH_PROJECT', 'default')
        
        print(f"✅ Client created for project: {project_name}")
        
        # Create a trace directly
        trace_data = {
            "name": "direct_test_trace",
            "run_type": "chain",
            "inputs": {"question": "What are high-risk AI systems under the EU AI Act?"},
            "outputs": {"answer": "High-risk AI systems include those used in critical infrastructure, education, employment, and law enforcement."},
            "project_name": project_name,
            "tags": ["test", "direct", "eu-ai-act"],
            "metadata": {
                "source": "direct_test_script",
                "llm_provider": "test"
            }
        }
        
        # Create the trace
        trace = client.create_run(**trace_data)
        
        print(f"✅ Trace created successfully!")
        print(f"🔗 Trace ID: {trace.id}")
        print(f"🌐 Trace URL: https://smith.langchain.com/trace/{trace.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_direct_trace()
