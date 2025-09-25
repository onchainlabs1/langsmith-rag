"""Tests for EU AI Act compliance RAG system."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.app.retrieval.index_ai_act import AIActIndexer
from src.app.services.llm import ComplianceLLMService
from src.app.services.rag_pipeline import ComplianceRAGPipeline
from src.evals.compliance_evaluators import ComplianceEvaluationService


class TestAIActIndexer:
    """Test AI Act corpus indexer."""
    
    def test_initialization(self):
        """Test indexer initialization."""
        indexer = AIActIndexer()
        assert indexer.embeddings is not None
        assert indexer.text_splitter is not None
        assert indexer.logger is not None
    
    def test_extract_risk_category(self):
        """Test risk category extraction."""
        indexer = AIActIndexer()
        
        # Test prohibited content
        prohibited_content = "This document discusses prohibited AI practices..."
        assert indexer._extract_risk_category(prohibited_content) == "prohibited"
        
        # Test high-risk content
        high_risk_content = "High-risk AI systems require special attention..."
        assert indexer._extract_risk_category(high_risk_content) == "high-risk"
        
        # Test general content
        general_content = "This is a general document about AI systems..."
        assert indexer._extract_risk_category(general_content) == "general"
    
    def test_extract_article_references(self):
        """Test article reference extraction."""
        indexer = AIActIndexer()
        
        content = "According to Article 5, AI systems must comply with requirements. Art. 10 specifies additional obligations."
        references = indexer._extract_article_references(content)
        
        assert "Article 5" in references
        assert "Article 10" in references
        assert len(references) == 2
    
    def test_extract_compliance_keywords(self):
        """Test compliance keyword extraction."""
        indexer = AIActIndexer()
        
        content = "This document discusses risk management, safety requirements, and compliance obligations."
        keywords = indexer._extract_compliance_keywords(content)
        
        assert "risk" in keywords
        assert "safety" in keywords
        assert "compliance" in keywords
        assert len(keywords) >= 3


class TestComplianceLLMService:
    """Test compliance-focused LLM service."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = ComplianceLLMService()
        assert service.llm is not None
        assert service.system_prompt is not None
        assert "compliance" in service.system_prompt.lower()
    
    def test_system_prompt_creation(self):
        """Test system prompt creation."""
        service = ComplianceLLMService()
        prompt = service._create_compliance_system_prompt()
        
        assert "EU AI Act" in prompt
        assert "compliance" in prompt.lower()
        assert "risk" in prompt.lower()
        assert "transparency" in prompt.lower()
    
    @patch('src.app.services.llm.OpenAI')
    def test_generate_compliance_answer(self, mock_openai):
        """Test compliance answer generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.content = "This is a compliance-focused answer about EU AI Act requirements."
        mock_openai.return_value.invoke.return_value = mock_response
        
        service = ComplianceLLMService()
        context = [{"page_content": "AI Act content", "metadata": {"source": "test.md"}}]
        
        result = service.generate_compliance_answer("Test question", context)
        
        assert "answer" in result
        assert "compliance_focus" in result
        assert result["compliance_focus"] is True
    
    def test_validate_compliance_answer(self):
        """Test compliance answer validation."""
        service = ComplianceLLMService()
        
        # Test compliance-focused answer
        compliance_answer = "This answer discusses compliance obligations and risk assessment requirements."
        validation = service.validate_compliance_answer(compliance_answer, "Test question")
        
        assert validation["is_compliance_focused"] is True
        assert validation["confidence_score"] > 0.5
        
        # Test non-compliance answer
        non_compliance_answer = "This is a general answer about AI systems."
        validation = service.validate_compliance_answer(non_compliance_answer, "Test question")
        
        assert validation["is_compliance_focused"] is False
        assert validation["confidence_score"] < 0.5


class TestComplianceRAGPipeline:
    """Test compliance RAG pipeline."""
    
    def test_initialization(self):
        """Test pipeline initialization."""
        mock_vectorstore = Mock()
        pipeline = ComplianceRAGPipeline(mock_vectorstore)
        
        assert pipeline.vectorstore_service == mock_vectorstore
        assert pipeline.llm_service is not None
        assert pipeline.langsmith_client is not None
    
    @patch('src.app.services.rag_pipeline.Client')
    def test_answer_compliance_question(self, mock_client):
        """Test compliance question answering."""
        # Mock vectorstore service
        mock_vectorstore = Mock()
        mock_vectorstore.vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [
            (Mock(page_content="AI Act content", metadata={"source": "test.md"}), 0.8)
        ]
        
        # Mock LLM service
        mock_llm_service = Mock()
        mock_llm_service.generate_compliance_answer.return_value = {
            "answer": "Compliance answer",
            "model": "gpt-3.5-turbo",
            "temperature": 0.1,
            "compliance_focus": True
        }
        
        pipeline = ComplianceRAGPipeline(mock_vectorstore)
        pipeline.llm_service = mock_llm_service
        
        # Mock LangSmith client
        mock_trace = Mock()
        mock_trace.id = "test-trace-id"
        mock_client.return_value.trace.return_value.__enter__.return_value = mock_trace
        
        result = pipeline.answer_compliance_question("What are the prohibited practices?")
        
        assert "answer" in result
        assert "sources" in result
        assert "trace_url" in result
        assert "compliance_metadata" in result
    
    def test_calculate_compliance_relevance(self):
        """Test compliance relevance calculation."""
        mock_vectorstore = Mock()
        pipeline = ComplianceRAGPipeline(mock_vectorstore)
        
        # Test high relevance document
        high_relevance_doc = Mock()
        high_relevance_doc.page_content = "This document discusses compliance obligations, risk assessment, and audit requirements."
        high_relevance_doc.metadata = {}
        
        relevance = pipeline._calculate_compliance_relevance(high_relevance_doc)
        assert relevance == "high"
        
        # Test low relevance document
        low_relevance_doc = Mock()
        low_relevance_doc.page_content = "This is a general document about AI systems."
        low_relevance_doc.metadata = {}
        
        relevance = pipeline._calculate_compliance_relevance(low_relevance_doc)
        assert relevance == "low"
    
    def test_extract_risk_implications(self):
        """Test risk implications extraction."""
        mock_vectorstore = Mock()
        pipeline = ComplianceRAGPipeline(mock_vectorstore)
        
        # Test document with risk implications
        doc = Mock()
        doc.page_content = "This document discusses high-risk AI systems, safety requirements, and privacy protection measures."
        doc.metadata = {}
        
        implications = pipeline._extract_risk_implications(doc)
        
        assert "high_risk_systems" in implications
        assert "safety_security" in implications
        assert "privacy_data_protection" in implications


class TestComplianceEvaluationService:
    """Test compliance evaluation service."""
    
    def test_initialization(self):
        """Test evaluation service initialization."""
        mock_pipeline = Mock()
        service = ComplianceEvaluationService(mock_pipeline)
        
        assert service.compliance_pipeline == mock_pipeline
        assert service.langsmith_client is not None
    
    def test_evaluate_groundedness(self):
        """Test groundedness evaluation."""
        mock_pipeline = Mock()
        service = ComplianceEvaluationService(mock_pipeline)
        
        sources = [Mock(content="AI Act content about compliance requirements")]
        score = service._evaluate_groundedness("Test question", "Answer about compliance", sources)
        
        assert 0.0 <= score <= 1.0
    
    def test_evaluate_correctness(self):
        """Test correctness evaluation."""
        mock_pipeline = Mock()
        service = ComplianceEvaluationService(mock_pipeline)
        
        score = service._evaluate_correctness(
            "Test question",
            "Answer about compliance requirements",
            "Reference about compliance requirements"
        )
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should have good overlap
    
    def test_evaluate_compliance_focus(self):
        """Test compliance focus evaluation."""
        mock_pipeline = Mock()
        service = ComplianceEvaluationService(mock_pipeline)
        
        # Test compliance-focused answer
        compliance_answer = "This answer discusses compliance obligations, risk assessment, and audit requirements."
        score = service._evaluate_compliance_focus("Test question", compliance_answer, [])
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should have good compliance focus
        
        # Test non-compliance answer
        non_compliance_answer = "This is a general answer about AI systems."
        score = service._evaluate_compliance_focus("Test question", non_compliance_answer, [])
        
        assert score < 0.5  # Should have low compliance focus


class TestAIActAPI:
    """Test AI Act compliance API endpoints."""
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_compliance_answer_endpoint(self):
        """Test compliance answer endpoint."""
        with patch('src.api.routes.get_compliance_rag_pipeline') as mock_get_pipeline:
            # Mock compliance pipeline
            mock_pipeline = Mock()
            mock_pipeline.answer_compliance_question.return_value = {
                "answer": "Compliance-focused answer",
                "sources": [{"content": "AI Act content", "source": "test.md"}],
                "trace_url": "https://smith.langchain.com/trace/test",
                "request_id": "test-request-id",
                "compliance_metadata": {"compliance_focus": True}
            }
            mock_get_pipeline.return_value = mock_pipeline
            
            client = TestClient(app)
            response = client.post(
                "/v1/answer",
                json={"question": "What are the prohibited AI practices?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "sources" in data
            assert "trace_url" in data
            assert "request_id" in data
    
    def test_compliance_answer_validation(self):
        """Test compliance answer validation."""
        with patch('src.api.routes.get_compliance_rag_pipeline') as mock_get_pipeline:
            # Mock pipeline that raises exception
            mock_pipeline = Mock()
            mock_pipeline.answer_compliance_question.side_effect = Exception("Test error")
            mock_get_pipeline.return_value = mock_pipeline
            
            client = TestClient(app)
            response = client.post(
                "/v1/answer",
                json={"question": "Test question"}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "compliance question" in data["detail"]
