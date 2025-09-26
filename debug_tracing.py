#!/usr/bin/env python3
"""
Debug script to test LangSmith tracing
"""

import os
import sys
sys.path.append('src')

def test_environment():
    """Test environment variables."""
    print("🔍 Testing Environment Variables...")
    print("=" * 50)
    
    required_vars = [
        'LANGSMITH_API_KEY',
        'LANGSMITH_PROJECT',
        'LANGCHAIN_API_KEY',
        'LANGCHAIN_PROJECT'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "❌ Not set"
        print(f"  {var}: {status}")
        if value:
            print(f"    Value: {value[:20]}...")
        if not value:
            all_set = False
    
    return all_set

def test_langsmith_connection():
    """Test LangSmith connection."""
    print("\n🔗 Testing LangSmith Connection...")
    print("=" * 40)
    
    try:
        from langsmith import Client
        
        api_key = os.getenv('LANGSMITH_API_KEY')
        if not api_key:
            print("❌ LANGSMITH_API_KEY not found!")
            return False
        
        client = Client(api_key=api_key)
        print("✅ LangSmith client created")
        
        # List projects
        projects = list(client.list_projects())
        print(f"📁 Found {len(projects)} projects:")
        for project in projects:
            print(f"  - {project.name} (ID: {project.id})")
        
        # Check if our project exists
        target_project = os.getenv('LANGSMITH_PROJECT', 'default')
        project_exists = any(p.name == target_project for p in projects)
        
        if project_exists:
            print(f"✅ Target project '{target_project}' exists")
        else:
            print(f"⚠️ Target project '{target_project}' not found")
            print("   Available projects listed above")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_simple_trace():
    """Test creating a simple trace."""
    print("\n🧪 Testing Simple Trace Creation...")
    print("=" * 45)
    
    try:
        from langsmith import Client
        
        client = Client(api_key=os.getenv('LANGSMITH_API_KEY'))
        project_name = os.getenv('LANGSMITH_PROJECT', 'default')
        
        # Create a simple trace using the correct API
        trace = client.create_run(
            name="debug_test_trace",
            run_type="chain",
            inputs={"test": "Debug test from langsmith-rag"},
            project_name=project_name,
            tags=["debug", "test", "langsmith-rag"],
            metadata={"source": "debug_script"}
        )
        
        if trace and hasattr(trace, 'id'):
            # Simulate some work
            result = "Debug test completed successfully"
            
            # Update trace with outputs
            client.update_run(
                run_id=trace.id,
                outputs={"result": result}
            )
                
            print(f"✅ Trace created successfully!")
            print(f"🔗 Trace ID: {trace.id}")
            print(f"🌐 Trace URL: https://smith.langchain.com/trace/{trace.id}")
            print(f"📁 Project: {project_name}")
        else:
            print(f"❌ Failed to create trace: {trace}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating trace: {str(e)}")
        return False

def test_rag_tracing():
    """Test RAG system tracing."""
    print("\n🚀 Testing RAG System Tracing...")
    print("=" * 40)
    
    try:
        from src.services.groq_langchain_rag import GroqLangChainRAG
        
        print("✅ Imported GroqLangChainRAG")
        
        # Initialize RAG system
        rag = GroqLangChainRAG()
        print("✅ RAG system initialized")
        
        # Load documents
        rag.load_documents()
        print("✅ Documents loaded")
        
        # Ask a question
        print("❓ Asking question...")
        result = rag.answer_question("What are high-risk AI systems under the EU AI Act?")
        
        print(f"✅ Question answered!")
        print(f"📝 Answer length: {len(result['answer'])} characters")
        print(f"🔗 Trace URL: {result.get('trace_url', 'Not available')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with RAG system: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function."""
    print("🐛 LangSmith Tracing Debug Script")
    print("=" * 60)
    
    # Test 1: Environment variables
    env_ok = test_environment()
    
    # Test 2: LangSmith connection
    connection_ok = test_langsmith_connection()
    
    # Test 3: Simple trace
    simple_trace_ok = test_simple_trace()
    
    # Test 4: RAG tracing
    rag_trace_ok = test_rag_tracing()
    
    # Summary
    print("\n📊 Debug Summary:")
    print("=" * 30)
    print(f"  Environment: {'✅ OK' if env_ok else '❌ Failed'}")
    print(f"  Connection: {'✅ OK' if connection_ok else '❌ Failed'}")
    print(f"  Simple Trace: {'✅ OK' if simple_trace_ok else '❌ Failed'}")
    print(f"  RAG Trace: {'✅ OK' if rag_trace_ok else '❌ Failed'}")
    
    if all([env_ok, connection_ok, simple_trace_ok, rag_trace_ok]):
        print("\n🎉 All tests passed! Tracing should be working.")
    else:
        print("\n🔧 Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
