#!/usr/bin/env python3
"""Test script to verify the EU AI Act Compliance RAG System interface."""

import sys
import os
import requests
import time
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit import OK")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import src.core.auth
        print("✅ Auth module import OK")
    except ImportError as e:
        print(f"❌ Auth module import failed: {e}")
        return False
    
    try:
        import src.core.observability
        print("✅ Observability module import OK")
    except ImportError as e:
        print(f"❌ Observability module import failed: {e}")
        return False
    
    try:
        import ui_app
        print("✅ UI app import OK")
    except ImportError as e:
        print(f"❌ UI app import failed: {e}")
        return False
    
    return True

def test_docker_compose():
    """Test if Docker Compose configuration is valid."""
    print("\n🐳 Testing Docker Compose configuration...")
    
    try:
        import subprocess
        result = subprocess.run(['docker', 'compose', 'config'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Docker Compose configuration is valid")
            return True
        else:
            print(f"❌ Docker Compose configuration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Docker Compose test failed: {e}")
        return False

def test_ui_app():
    """Test if the UI app can be loaded."""
    print("\n🖥️ Testing UI app...")
    
    try:
        # Test if the UI app can be imported and basic functions work
        import ui_app
        print("✅ UI app can be imported")
        
        # Test if Streamlit can be initialized (without running)
        import streamlit as st
        print("✅ Streamlit can be initialized")
        
        return True
    except Exception as e:
        print(f"❌ UI app test failed: {e}")
        return False

def test_environment():
    """Test environment setup."""
    print("\n🌍 Testing environment...")
    
    # Check if required files exist
    required_files = [
        'ui_app.py',
        'src/core/auth.py',
        'src/core/observability.py',
        'docker-compose.yml',
        'Makefile'
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 EU AI Act Compliance RAG System - Interface Test")
    print("=" * 60)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Docker Compose", test_docker_compose),
        ("UI App", test_ui_app)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! The interface should work correctly.")
        print("\n📋 Next steps:")
        print("1. Set up your API keys in .env file")
        print("2. Run: make compose-up")
        print("3. Access UI at: http://localhost:8501")
        print("4. Access API at: http://localhost:8000")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Check Python version: python3 --version")
        print("3. Check Docker: docker --version")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
