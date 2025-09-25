"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_answer_endpoint_success(client):
    """Test successful answer endpoint."""
    # Mock the RAG service to avoid actual LLM calls in tests
    with pytest.MonkeyPatch().context() as m:
        # Mock the RAG service
        m.setattr("src.api.routes.get_rag_service", lambda: None)
        
        # Mock the answer_question method
        class MockRAGService:
            def answer_question(self, question, request_id=None):
                return {
                    "answer": "Test answer",
                    "sources": [{"content": "Test content", "source": "test.md", "filename": "test.md"}],
                    "trace_url": "https://smith.langchain.com/trace/test",
                    "request_id": "test-request-id"
                }
        
        m.setattr("src.api.routes.get_rag_service", lambda: MockRAGService())
        
        response = client.post(
            "/v1/answer",
            json={"question": "What is ISO 42001?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "trace_url" in data
        assert "request_id" in data


def test_answer_endpoint_validation(client):
    """Test answer endpoint validation."""
    # Test empty question
    response = client.post("/v1/answer", json={"question": ""})
    assert response.status_code == 422
    
    # Test missing question
    response = client.post("/v1/answer", json={})
    assert response.status_code == 422


def test_answer_endpoint_error_handling(client):
    """Test answer endpoint error handling."""
    with pytest.MonkeyPatch().context() as m:
        # Mock the RAG service to raise an exception
        class MockRAGService:
            def answer_question(self, question, request_id=None):
                raise Exception("Test error")
        
        m.setattr("src.api.routes.get_rag_service", lambda: MockRAGService())
        
        response = client.post(
            "/v1/answer",
            json={"question": "What is ISO 42001?"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
