"""Service layer tests."""

import pytest
from unittest.mock import Mock, patch

from src.services.vectorstore import VectorStoreService
from src.services.rag import RAGService
from src.evals.evaluators import EvaluationService


class TestVectorStoreService:
    """Test vectorstore service."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = VectorStoreService()
        assert service.embeddings is not None
        assert service.text_splitter is not None
        assert service.vectorstore is None
    
    @patch('src.services.vectorstore.FAISS.from_documents')
    def test_load_knowledge_base(self, mock_faiss):
        """Test loading knowledge base."""
        # Mock FAISS
        mock_vectorstore = Mock()
        mock_faiss.return_value = mock_vectorstore
        
        service = VectorStoreService()
        
        # Create test knowledge directory
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test markdown file
            test_file = os.path.join(temp_dir, "test.md")
            with open(test_file, "w") as f:
                f.write("# Test Document\n\nThis is a test document.")
            
            service.load_knowledge_base(temp_dir)
            
            # Verify FAISS was called
            mock_faiss.assert_called_once()
            assert service.vectorstore == mock_vectorstore


class TestRAGService:
    """Test RAG service."""
    
    def test_initialization(self):
        """Test service initialization."""
        mock_vectorstore = Mock()
        service = RAGService(mock_vectorstore)
        
        assert service.vectorstore_service == mock_vectorstore
        assert service.llm is not None
        assert service.langsmith_client is not None
        assert service.retrieval_chain is not None
    
    @patch('src.services.rag.Client')
    def test_answer_question(self, mock_client):
        """Test answering questions."""
        # Mock vectorstore service
        mock_vectorstore = Mock()
        mock_retriever = Mock()
        mock_vectorstore.get_retriever.return_value = mock_retriever
        
        # Mock retrieval chain
        mock_chain = Mock()
        mock_chain.return_value = {
            "result": "Test answer",
            "source_documents": [
                Mock(page_content="Test content", metadata={"source": "test.md", "filename": "test.md"})
            ]
        }
        
        service = RAGService(mock_vectorstore)
        service.retrieval_chain = mock_chain
        
        # Mock LangSmith client
        mock_trace = Mock()
        mock_trace.id = "test-trace-id"
        mock_client.return_value.trace.return_value.__enter__.return_value = mock_trace
        
        result = service.answer_question("What is ISO 42001?")
        
        assert result["answer"] == "Test answer"
        assert len(result["sources"]) == 1
        assert result["trace_url"] == "https://smith.langchain.com/trace/test-trace-id"
        assert "request_id" in result


class TestEvaluationService:
    """Test evaluation service."""
    
    def test_initialization(self):
        """Test service initialization."""
        mock_rag_service = Mock()
        service = EvaluationService(mock_rag_service)
        
        assert service.rag_service == mock_rag_service
        assert service.langsmith_client is not None
    
    def test_evaluate_groundedness(self):
        """Test groundedness evaluation."""
        mock_rag_service = Mock()
        service = EvaluationService(mock_rag_service)
        
        # Test with good grounding
        sources = [Mock(content="ISO 42001 is the AI management system standard")]
        score = service._evaluate_groundedness(
            question="What is ISO 42001?",
            answer="ISO 42001 is the AI management system standard",
            sources=sources
        )
        assert score > 0.5
        
        # Test with poor grounding
        sources = [Mock(content="Different content")]
        score = service._evaluate_groundedness(
            question="What is ISO 42001?",
            answer="ISO 42001 is the AI management system standard",
            sources=sources
        )
        assert score < 0.5
    
    def test_evaluate_correctness(self):
        """Test correctness evaluation."""
        mock_rag_service = Mock()
        service = EvaluationService(mock_rag_service)
        
        # Test with good correctness
        score = service._evaluate_correctness(
            question="What is ISO 42001?",
            answer="ISO 42001 is the AI management system standard",
            reference="ISO 42001 is the AI management system standard"
        )
        assert score > 0.5
        
        # Test with poor correctness
        score = service._evaluate_correctness(
            question="What is ISO 42001?",
            answer="Different answer",
            reference="ISO 42001 is the AI management system standard"
        )
        assert score < 0.5
