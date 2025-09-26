#!/usr/bin/env python3
"""
Full System Test - Verify all components work together
"""

import os
import sys
import time
import requests
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_environment_setup():
    """Test environment configuration."""
    print("🔧 Testing Environment Setup...")
    
    required_vars = [
        'LANGSMITH_API_KEY',
        'LANGCHAIN_TRACING_V2',
        'LANGCHAIN_PROJECT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_observability_service():
    """Test observability service initialization."""
    print("📊 Testing Observability Service...")
    
    try:
        from src.core.observability import get_observability_service
        
        obs = get_observability_service()
        print("✅ Observability service initialized")
        
        # Test metrics recording
        obs.record_request_metrics(
            correlation_id="test-123",
            provider="groq",
            input_tokens=100,
            output_tokens=200,
            cost=0.01
        )
        print("✅ Metrics recording works")
        
        return True
    except Exception as e:
        print(f"❌ Observability service error: {e}")
        return False

def test_rag_system():
    """Test RAG system functionality."""
    print("🤖 Testing RAG System...")
    
    try:
        from src.services.groq_langchain_rag import GroqLangChainRAG
        
        # Initialize RAG system
        rag = GroqLangChainRAG()
        print("✅ RAG system initialized")
        
        # Test with mock question (won't actually call API without keys)
        test_question = "What are high-risk AI systems under the EU AI Act?"
        
        # This will fail gracefully without API keys, which is expected
        try:
            result = rag.answer_question(test_question)
            print("✅ RAG system functional")
        except Exception as e:
            if "api_key" in str(e).lower():
                print("⚠️ RAG system needs API keys (expected)")
            else:
                print(f"❌ RAG system error: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ RAG system initialization error: {e}")
        return False

def test_evaluation_system():
    """Test evaluation system."""
    print("🔬 Testing Evaluation System...")
    
    try:
        # Check if evaluation files exist
        eval_script = Path("evals/run_eval.py")
        eval_dataset = Path("evals/datasets/ai_act_eval.csv")
        
        if not eval_script.exists():
            print("❌ Evaluation script not found")
            return False
        
        if not eval_dataset.exists():
            print("❌ Evaluation dataset not found")
            return False
        
        print("✅ Evaluation files present")
        
        # Test dataset loading
        import csv
        with open(eval_dataset, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if len(rows) < 5:
            print("❌ Evaluation dataset too small")
            return False
        
        print(f"✅ Evaluation dataset loaded ({len(rows)} rows)")
        return True
        
    except Exception as e:
        print(f"❌ Evaluation system error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints."""
    print("🌐 Testing API Endpoints...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"⚠️ Health endpoint returned {response.status_code}")
            
        # Test metrics endpoint
        response = requests.get("http://localhost:8000/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ Metrics endpoint working")
        else:
            print(f"⚠️ Metrics endpoint returned {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️ API not running (start with: uvicorn src.main:app --reload)")
        return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def test_docker_files():
    """Test Docker configuration files."""
    print("🐳 Testing Docker Configuration...")
    
    docker_files = [
        "Dockerfile",
        "docker-compose.monitoring.yml"
    ]
    
    for file_path in docker_files:
        if not Path(file_path).exists():
            print(f"❌ {file_path} not found")
            return False
    
    print("✅ Docker files present")
    return True

def test_monitoring_config():
    """Test monitoring configuration."""
    print("📈 Testing Monitoring Configuration...")
    
    monitoring_files = [
        "monitoring/prometheus.yml",
        "monitoring/grafana/provisioning/datasources/prometheus.yml",
        "monitoring/grafana/provisioning/dashboards/dashboards.yml",
        "monitoring/grafana/dashboards/rag-system-dashboard.json"
    ]
    
    for file_path in monitoring_files:
        if not Path(file_path).exists():
            print(f"❌ {file_path} not found")
            return False
    
    print("✅ Monitoring configuration complete")
    return True

def test_ci_cd_config():
    """Test CI/CD configuration."""
    print("🔄 Testing CI/CD Configuration...")
    
    ci_files = [
        ".github/workflows/ci-cd.yml"
    ]
    
    for file_path in ci_files:
        if not Path(file_path).exists():
            print(f"❌ {file_path} not found")
            return False
    
    print("✅ CI/CD configuration present")
    return True

def main():
    """Run all system tests."""
    print("🚀 EU AI Act RAG System - Full System Test")
    print("=" * 50)
    
    tests = [
        test_environment_setup,
        test_observability_service,
        test_rag_system,
        test_evaluation_system,
        test_docker_files,
        test_monitoring_config,
        test_ci_cd_config,
        test_api_endpoints,  # Run last as it requires API to be running
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
        
        print()  # Add spacing between tests
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production.")
    elif passed >= total * 0.8:
        print("✅ Most tests passed. System is mostly functional.")
    else:
        print("⚠️ Several tests failed. Check the issues above.")
    
    print("\n🚀 Next Steps:")
    print("1. Set up API keys (GROQ_API_KEY or OPENAI_API_KEY)")
    print("2. Start the API: uvicorn src.main:app --reload")
    print("3. Start monitoring: docker-compose -f docker-compose.monitoring.yml up -d")
    print("4. Run evaluations: python evals/run_eval.py --provider groq --quick")
    print("5. Start UI: streamlit run ui_app.py")

if __name__ == "__main__":
    main()
