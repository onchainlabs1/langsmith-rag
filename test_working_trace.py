#!/usr/bin/env python3
"""
Working trace test using correct LangSmith API
"""

import os
from langsmith import Client

def test_working_trace():
    """Test working trace creation."""
    print("🧪 Testing Working LangSmith Trace...")
    
    try:
        # Create client
        client = Client(api_key=os.getenv('LANGSMITH_API_KEY'))
        project_name = os.getenv('LANGSMITH_PROJECT', 'default')
        
        print(f"✅ Client created for project: {project_name}")
        
        # Create a trace using the correct method
        trace = client.create_run(
            name="working_test_trace",
            run_type="chain",
            inputs={"question": "What are high-risk AI systems under the EU AI Act?"},
            project_name=project_name,
            tags=["test", "working", "eu-ai-act"],
            metadata={
                "source": "working_test_script",
                "llm_provider": "test"
            }
        )
        
        print(f"✅ Trace created: {trace}")
        
        if trace:
            # Update with outputs
            client.update_run(
                run_id=trace.id,
                outputs={"answer": "High-risk AI systems include those used in critical infrastructure, education, employment, and law enforcement."}
            )
            
            print(f"✅ Trace updated with outputs")
            print(f"🔗 Trace ID: {trace.id}")
            print(f"🌐 Trace URL: https://smith.langchain.com/trace/{trace.id}")
            
            return True
        else:
            print(f"❌ Trace creation returned None")
            return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_working_trace()
