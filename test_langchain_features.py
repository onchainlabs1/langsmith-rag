#!/usr/bin/env python3
"""Test script for advanced LangChain features."""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app.services.advanced_langchain import AdvancedLangChainService
from src.app.services.conversation_memory import AdvancedConversationMemory, memory_manager
from src.services.vectorstore import VectorStoreService


async def test_advanced_langchain():
    """Test advanced LangChain functionality."""
    print("🧪 Testing Advanced LangChain Features")
    print("=" * 50)
    
    try:
        # Initialize services
        vectorstore_service = VectorStoreService()
        advanced_langchain = AdvancedLangChainService(vectorstore_service)
        
        print("✅ Advanced LangChain service initialized")
        
        # Test streaming response
        print("\n🔍 Testing streaming response...")
        question = "What are the requirements for high-risk AI systems under the EU AI Act?"
        
        async for chunk in advanced_langchain.answer_question_streaming(
            question=question,
            use_conversation=False,
            max_sources=3
        ):
            if chunk.get("type") == "metadata":
                print(f"📋 Request ID: {chunk.get('request_id')}")
            elif chunk.get("type") == "sources":
                print(f"📚 Retrieved {chunk.get('num_sources')} sources")
            elif chunk.get("type") == "content":
                print(f"💬 Streaming: {chunk.get('content', '')[:50]}...")
            elif chunk.get("type") == "final":
                print("✅ Streaming completed successfully")
                break
        
        print("✅ Streaming test passed")
        
        # Test compliance insights
        print("\n📊 Testing compliance insights...")
        insights = advanced_langchain.get_compliance_insights(question)
        print(f"Risk categories: {insights.get('risk_categories', [])}")
        print(f"Article references: {insights.get('article_references', [])}")
        print("✅ Compliance insights test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced LangChain test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_memory():
    """Test conversation memory functionality."""
    print("\n🧠 Testing Conversation Memory")
    print("=" * 50)
    
    try:
        # Create conversation memory
        session_id = "test-session-123"
        memory = AdvancedConversationMemory(session_id, "test-user")
        
        print("✅ Conversation memory initialized")
        
        # Add some interactions
        questions_and_answers = [
            ("What is the EU AI Act?", "The EU AI Act is a comprehensive regulatory framework..."),
            ("What are high-risk systems?", "High-risk AI systems are those that pose significant risks..."),
            ("What are the compliance requirements?", "Compliance requirements include risk assessments...")
        ]
        
        for i, (question, answer) in enumerate(questions_and_answers):
            memory.add_interaction(
                question=question,
                answer=answer,
                sources=[{"content": f"Source {i+1}", "filename": f"doc{i+1}.md"}],
                compliance_metadata={
                    "risk_categories": ["high-risk", "limited-risk"],
                    "article_references": [f"Article {i+1}"],
                    "compliance_score": 0.8 + (i * 0.05)
                }
            )
            print(f"✅ Added interaction {i+1}")
        
        # Test conversation history
        history = memory.get_conversation_history("buffer")
        print(f"📝 Conversation history: {len(history)} messages")
        
        # Test conversation summary
        summary = memory.get_conversation_summary()
        print(f"📄 Summary: {summary[:100]}...")
        
        # Test context summary
        context = memory.get_context_summary()
        print(f"🎯 Risk categories: {context['risk_categories']}")
        print(f"📖 Article references: {context['article_references']}")
        
        # Test memory stats
        stats = memory.get_memory_stats()
        print(f"📊 Memory stats: {stats}")
        
        # Test export
        export_data = memory.export_conversation()
        print(f"💾 Export data keys: {list(export_data.keys())}")
        
        print("✅ Conversation memory test passed")
        return True
        
    except Exception as e:
        print(f"❌ Conversation memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_manager():
    """Test memory manager functionality."""
    print("\n🎛️ Testing Memory Manager")
    print("=" * 50)
    
    try:
        # Create multiple sessions
        session_ids = ["session-1", "session-2", "session-3"]
        
        for session_id in session_ids:
            memory = memory_manager.get_or_create_memory(session_id, f"user-{session_id}")
            memory.add_interaction(
                question=f"Question for {session_id}",
                answer=f"Answer for {session_id}",
                sources=[],
                compliance_metadata={}
            )
            print(f"✅ Created memory for {session_id}")
        
        # Test global stats
        global_stats = memory_manager.get_global_stats()
        print(f"📊 Global stats: {global_stats}")
        
        # Test session retrieval
        active_sessions = memory_manager.get_all_sessions()
        print(f"🔄 Active sessions: {active_sessions}")
        
        # Test cleanup
        memory_manager.cleanup_old_sessions(max_age_hours=0)  # Clean all
        remaining_sessions = memory_manager.get_all_sessions()
        print(f"🧹 Sessions after cleanup: {remaining_sessions}")
        
        print("✅ Memory manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Memory manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🚀 EU AI Act Compliance RAG - LangChain Features Test")
    print("=" * 60)
    
    # Test advanced LangChain
    langchain_success = await test_advanced_langchain()
    
    # Test conversation memory
    memory_success = test_conversation_memory()
    
    # Test memory manager
    manager_success = test_memory_manager()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"Advanced LangChain: {'PASS' if langchain_success else 'FAIL'}")
    print(f"Conversation Memory: {'PASS' if memory_success else 'FAIL'}")
    print(f"Memory Manager: {'PASS' if manager_success else 'FAIL'}")
    print("=" * 60)
    
    if langchain_success and memory_success and manager_success:
        print("🎉 All LangChain feature tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
