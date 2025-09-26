#!/usr/bin/env python3
"""Test script to verify LangSmith configuration."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_langsmith_config():
    """Test LangSmith configuration."""
    print("🔍 Testing LangSmith Configuration")
    print("=" * 50)
    
    # Check environment variables
    langchain_key = os.getenv("LANGCHAIN_API_KEY")
    langchain_project = os.getenv("LANGCHAIN_PROJECT", "default")
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false")
    
    print(f"LANGCHAIN_API_KEY: {'✅ Set' if langchain_key else '❌ Not set'}")
    if langchain_key:
        print(f"   Key format: {langchain_key[:10]}...")
    
    print(f"LANGCHAIN_PROJECT: {langchain_project}")
    print(f"LANGCHAIN_TRACING_V2: {tracing_enabled}")
    
    # Test LangSmith client
    try:
        from langsmith import Client
        
        if langchain_key:
            client = Client(api_key=langchain_key)
            
            # Test connection
            try:
                # Try to get projects (this will test the connection)
                projects = list(client.list_projects())
                print(f"✅ LangSmith connection successful")
                print(f"   Found {len(projects)} projects")
                
                # Check if our project exists
                project_names = [p.name for p in projects]
                if langchain_project in project_names:
                    print(f"✅ Project '{langchain_project}' exists")
                else:
                    print(f"ℹ️ Project '{langchain_project}' will be created on first trace")
                
            except Exception as e:
                print(f"❌ LangSmith connection failed: {e}")
                return False
        else:
            print("⚠️ No API key provided - LangSmith tracing will be disabled")
            return False
            
    except ImportError:
        print("❌ LangSmith client not installed")
        return False
    
    return True


def test_tracing_import():
    """Test if tracing imports work."""
    print("\n🧪 Testing Tracing Imports")
    print("=" * 50)
    
    try:
        from langsmith import Client
        print("✅ LangSmith Client import successful")
        
        # Test if we can create a client
        client = Client()
        print("✅ LangSmith Client creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ LangSmith import failed: {e}")
        return False


def show_setup_instructions():
    """Show setup instructions."""
    print("\n📋 LangSmith Setup Instructions")
    print("=" * 50)
    
    print("1. 🔑 Get API Key:")
    print("   - Go to: https://smith.langchain.com/")
    print("   - Login with GitHub")
    print("   - Settings > API Keys > Create API Key")
    print("   - Copy the key (starts with ls__...)")
    
    print("\n2. ⚙️ Configure Environment:")
    print("   export LANGCHAIN_API_KEY='your_langsmith_api_key_here'")
    print("   export LANGCHAIN_PROJECT='groq-eu-ai-act-compliance'")
    print("   export LANGCHAIN_TRACING_V2='true'")
    
    print("\n3. 🧪 Test Configuration:")
    print("   python3 test_langsmith_config.py")
    
    print("\n4. 🚀 Start Application:")
    print("   uvicorn src.main:app --reload")
    
    print("\n5. 📊 View Traces:")
    print("   - Go to: https://smith.langchain.com/")
    print("   - Select your project")
    print("   - View traces in real-time")


def main():
    """Run LangSmith configuration test."""
    print("🚀 LangSmith Configuration Test")
    print("=" * 60)
    
    # Test imports
    import_success = test_tracing_import()
    
    # Test configuration
    config_success = test_langsmith_config()
    
    # Show instructions
    show_setup_instructions()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"LangSmith Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"LangSmith Config: {'✅ PASS' if config_success else '❌ FAIL'}")
    print("=" * 60)
    
    if config_success:
        print("🎉 LangSmith is properly configured!")
        print("   Traces will be sent to LangSmith automatically")
    else:
        print("⚠️ LangSmith needs configuration")
        print("   Follow the setup instructions above")
    
    return 0 if config_success else 1


if __name__ == "__main__":
    sys.exit(main())
