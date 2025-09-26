#!/usr/bin/env python3
"""
Final tracing test - simple and direct
"""

import os

def test_final_tracing():
    """Final test of LangSmith tracing."""
    print("🎯 Final LangSmith Tracing Test")
    print("=" * 50)
    
    # Configure environment for automatic tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "default"
    os.environ["LANGCHAIN_API_KEY"] = "your_langchain_api_key_here"
    
    print("✅ Environment configured for automatic tracing")
    print(f"  LANGCHAIN_TRACING_V2: {os.environ.get('LANGCHAIN_TRACING_V2')}")
    print(f"  LANGCHAIN_PROJECT: {os.environ.get('LANGCHAIN_PROJECT')}")
    print(f"  LANGCHAIN_API_KEY: {'Set' if os.environ.get('LANGCHAIN_API_KEY') else 'Not set'}")
    
    try:
        # Test 1: Simple LangChain run
        print("\n🧪 Test 1: Simple LangChain Runnable")
        print("-" * 40)
        
        from langchain_core.runnables import RunnableLambda
        
        def simple_function(inputs):
            return {"result": f"Processed: {inputs['text']}"}
        
        runnable = RunnableLambda(simple_function)
        result1 = runnable.invoke({"text": "Hello LangSmith!"})
        
        print(f"✅ Result 1: {result1}")
        
        # Test 2: Chain of operations
        print("\n🧪 Test 2: Chain of Operations")
        print("-" * 40)
        
        def step1(inputs):
            return {"step1": f"Step 1 processed: {inputs['text']}"}
        
        def step2(inputs):
            return {"step2": f"Step 2 processed: {inputs['step1']}"}
        
        def step3(inputs):
            return {"final": f"Final result: {inputs['step2']}"}
        
        chain = RunnableLambda(step1) | RunnableLambda(step2) | RunnableLambda(step3)
        result2 = chain.invoke({"text": "Chain test"})
        
        print(f"✅ Result 2: {result2}")
        
        # Test 3: RAG-like simulation
        print("\n🧪 Test 3: RAG-like Simulation")
        print("-" * 40)
        
        def rag_simulation(inputs):
            question = inputs["question"]
            # Simulate retrieval
            docs = ["EU AI Act Article 6", "EU AI Act Article 7"]
            # Simulate generation
            answer = f"Based on the EU AI Act, high-risk AI systems include those used in critical infrastructure, education, employment, and law enforcement. (Sources: {', '.join(docs)})"
            
            return {
                "question": question,
                "answer": answer,
                "sources": docs,
                "timestamp": "2025-01-27T12:00:00Z"
            }
        
        rag_runnable = RunnableLambda(rag_simulation)
        result3 = rag_runnable.invoke({"question": "What are high-risk AI systems under the EU AI Act?"})
        
        print(f"✅ Result 3: {result3['answer'][:100]}...")
        print(f"📚 Sources: {result3['sources']}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n📊 Next Steps:")
        print("1. Go to LangSmith dashboard: https://smith.langchain.com")
        print("2. Check the 'default' project")
        print("3. Look for traces with the following names:")
        print("   - simple_function")
        print("   - step1, step2, step3")
        print("   - rag_simulation")
        print("\n🔗 Direct link to project: https://smith.langchain.com/o/default/projects/default")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_final_tracing()
