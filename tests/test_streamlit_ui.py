"""Tests for Streamlit UI functionality."""

import pytest
from unittest.mock import Mock, patch
import requests


class TestStreamlitUI:
    """Test Streamlit UI components."""
    
    def test_check_api_health_success(self):
        """Test successful API health check."""
        from ui_app import check_api_health
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = check_api_health("http://localhost:8000/v1/answer")
            assert result is True
    
    def test_check_api_health_failure(self):
        """Test failed API health check."""
        from ui_app import check_api_health
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            
            result = check_api_health("http://localhost:8000/v1/answer")
            assert result is False
    
    def test_query_api_success(self):
        """Test successful API query."""
        from ui_app import query_api
        
        mock_response_data = {
            "answer": "Test compliance answer",
            "sources": [{"content": "Test source", "filename": "test.md"}],
            "trace_url": "https://smith.langchain.com/trace/test"
        }
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            result = query_api("http://localhost:8000/v1/answer", "Test question")
            
            assert result == mock_response_data
            mock_post.assert_called_once_with(
                "http://localhost:8000/v1/answer",
                json={"question": "Test question"},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
    
    def test_query_api_connection_error(self):
        """Test API query with connection error."""
        from ui_app import query_api
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError()
            
            result = query_api("http://localhost:8000/v1/answer", "Test question")
            assert result is None
    
    def test_query_api_timeout(self):
        """Test API query with timeout."""
        from ui_app import query_api
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout()
            
            result = query_api("http://localhost:8000/v1/answer", "Test question")
            assert result is None
    
    def test_query_api_http_error(self):
        """Test API query with HTTP error."""
        from ui_app import query_api
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            result = query_api("http://localhost:8000/v1/answer", "Test question")
            assert result is None
    
    def test_display_answer(self):
        """Test answer display functionality."""
        from ui_app import display_answer
        
        answer_data = {
            "answer": "Test compliance answer",
            "sources": [
                {
                    "content": "Test source content",
                    "filename": "test.md",
                    "source": "test.md",
                    "compliance_relevance": "high",
                    "risk_implications": ["high_risk_systems"],
                    "similarity_score": 0.85
                }
            ],
            "trace_url": "https://smith.langchain.com/trace/test",
            "compliance_metadata": {
                "validation": {
                    "is_compliance_focused": True,
                    "mentions_risk_categories": True,
                    "includes_citations": True,
                    "confidence_score": 0.9
                },
                "model": "gpt-3.5-turbo",
                "temperature": 0.1
            }
        }
        
        # This test verifies the function doesn't raise exceptions
        # In a real test environment, you'd use Streamlit's testing utilities
        try:
            display_answer(answer_data)
            assert True  # Function executed without errors
        except Exception as e:
            pytest.fail(f"display_answer raised an exception: {e}")
    
    def test_initialize_session_state(self):
        """Test session state initialization."""
        from ui_app import initialize_session_state
        
        # Mock streamlit session state
        with patch('streamlit.session_state', {}) as mock_session_state:
            initialize_session_state()
            
            # Verify session state is initialized
            assert 'query_history' in mock_session_state
            assert 'api_available' in mock_session_state
            assert mock_session_state['query_history'] == []
            assert mock_session_state['api_available'] is None
    
    def test_display_query_history(self):
        """Test query history display."""
        from ui_app import display_query_history
        
        # Mock streamlit components
        with patch('streamlit.session_state', {'query_history': ['Test question 1', 'Test question 2']}):
            with patch('streamlit.sidebar') as mock_sidebar:
                with patch('streamlit.button') as mock_button:
                    mock_button.return_value = False
                    
                    # This test verifies the function doesn't raise exceptions
                    try:
                        display_query_history()
                        assert True  # Function executed without errors
                    except Exception as e:
                        pytest.fail(f"display_query_history raised an exception: {e}")


class TestStreamlitIntegration:
    """Test Streamlit integration scenarios."""
    
    def test_full_workflow_simulation(self):
        """Test complete workflow simulation."""
        from ui_app import check_api_health, query_api
        
        # Test API health check
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            health_result = check_api_health("http://localhost:8000/v1/answer")
            assert health_result is True
        
        # Test API query
        mock_response_data = {
            "answer": "High-risk AI systems are those that pose significant risks to health, safety, or fundamental rights.",
            "sources": [
                {
                    "content": "High-risk AI systems must comply with strict requirements...",
                    "filename": "high_risk_systems.md",
                    "compliance_relevance": "high"
                }
            ],
            "trace_url": "https://smith.langchain.com/trace/123",
            "compliance_metadata": {
                "validation": {
                    "is_compliance_focused": True,
                    "confidence_score": 0.95
                }
            }
        }
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            query_result = query_api("http://localhost:8000/v1/answer", "What are high-risk AI systems?")
            
            assert query_result == mock_response_data
            assert query_result["answer"] == mock_response_data["answer"]
            assert len(query_result["sources"]) == 1
            assert query_result["trace_url"] == "https://smith.langchain.com/trace/123"
