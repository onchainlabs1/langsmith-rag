"""Compliance-focused RAG pipeline with LangSmith tracing and advanced LangChain features."""

import uuid
import logging
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator

from langsmith import Client
from langchain.schema import Document

from src.core.config import settings
from src.services.vectorstore import VectorStoreService
from src.app.services.llm import ComplianceLLMService
from src.app.services.advanced_langchain import AdvancedLangChainService
from src.app.services.conversation_memory import memory_manager
from src.core.observability import get_observability_service


class ComplianceRAGPipeline:
    """RAG pipeline specialized for EU AI Act compliance questions."""
    
    def __init__(self, vectorstore_service: VectorStoreService) -> None:
        """Initialize compliance RAG pipeline."""
        self.vectorstore_service = vectorstore_service
        self.llm_service = ComplianceLLMService()
        self.advanced_langchain = AdvancedLangChainService(vectorstore_service)
        self.langsmith_client = Client()
        self.observability = get_observability_service()
        self.logger = logging.getLogger(__name__)
        
    def answer_compliance_question(
        self, 
        question: str, 
        request_id: str | None = None,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """Answer EU AI Act compliance question with LangSmith tracing."""
        if request_id is None:
            request_id = str(uuid.uuid4())
            
        # Create LangSmith run for tracing
        with self.langsmith_client.trace(
            name="compliance_rag_pipeline",
            run_type="chain",
            inputs={"question": question, "request_id": request_id},
            project_name=settings.langchain_project,
            tags=["rag", "compliance", "ai_act", "production"],
            metadata={"request_id": request_id, "compliance_focus": True}
        ) as trace:
            try:
                # Step 1: Retrieve relevant documents
                self.logger.info(f"Retrieving documents for question: {question[:100]}...")
                retrieved_docs = self._retrieve_documents(question, max_sources)
                
                # Log retrieval results
                trace.metadata["retrieval_count"] = len(retrieved_docs)
                trace.metadata["retrieval_sources"] = [
                    doc.metadata.get("filename", "unknown") for doc in retrieved_docs
                ]
                
                # Step 2: Generate compliance-focused answer
                self.logger.info("Generating compliance-focused answer...")
                answer_result = self.llm_service.generate_compliance_answer(
                    question=question,
                    context=retrieved_docs,
                    request_id=request_id
                )
                
                # Step 3: Format sources with compliance metadata
                sources = self._format_sources_with_compliance_info(retrieved_docs)
                
                # Step 4: Validate answer quality
                validation = self.llm_service.validate_compliance_answer(
                    answer_result["answer"], question
                )
                
                # Prepare final result
                result = {
                    "answer": answer_result["answer"],
                    "sources": sources,
                    "trace_url": f"https://smith.langchain.com/trace/{trace.id}",
                    "request_id": request_id,
                    "compliance_metadata": {
                        "validation": validation,
                        "model": answer_result["model"],
                        "temperature": answer_result["temperature"],
                        "compliance_focus": answer_result["compliance_focus"]
                    }
                }
                
                # Log trace outputs
                trace.outputs = {
                    "answer": result["answer"],
                    "sources": sources,
                    "num_sources": len(sources),
                    "compliance_metadata": result["compliance_metadata"]
                }
                
                self.logger.info(f"Successfully generated compliance answer for request {request_id}")
                return result
                
            except Exception as e:
                self.logger.error(f"Error in compliance RAG pipeline: {e}")
                trace.error = str(e)
                raise
    
    def _retrieve_documents(self, question: str, max_sources: int) -> List[Document]:
        """Retrieve relevant documents for compliance question."""
        if self.vectorstore_service.vectorstore is None:
            raise ValueError("Vectorstore not initialized")
            
        # Perform similarity search
        docs_with_scores = self.vectorstore_service.similarity_search(
            query=question, 
            k=max_sources
        )
        
        # Filter and enhance documents
        filtered_docs = []
        for doc, score in docs_with_scores:
            # Enhance document with compliance metadata
            enhanced_doc = self._enhance_document_with_compliance_info(doc, score)
            filtered_docs.append(enhanced_doc)
            
        return filtered_docs
    
    def _enhance_document_with_compliance_info(self, doc: Document, score: float) -> Document:
        """Enhance document with compliance-specific information."""
        # Add compliance metadata
        if not hasattr(doc, 'metadata') or doc.metadata is None:
            doc.metadata = {}
            
        doc.metadata.update({
            "similarity_score": score,
            "compliance_relevance": self._calculate_compliance_relevance(doc),
            "risk_implications": self._extract_risk_implications(doc)
        })
        
        return doc
    
    def _calculate_compliance_relevance(self, doc: Document) -> str:
        """Calculate compliance relevance of document."""
        content = doc.page_content.lower()
        metadata = doc.metadata or {}
        
        # Check for compliance indicators
        compliance_indicators = [
            "compliance", "obligation", "requirement", "regulation",
            "conformity", "assessment", "audit", "monitoring"
        ]
        
        relevance_score = sum(1 for indicator in compliance_indicators if indicator in content)
        
        if relevance_score >= 3:
            return "high"
        elif relevance_score >= 1:
            return "medium"
        else:
            return "low"
    
    def _extract_risk_implications(self, doc: Document) -> List[str]:
        """Extract risk implications from document."""
        content = doc.page_content.lower()
        metadata = doc.metadata or {}
        
        risk_implications = []
        
        # Check for risk categories
        if "prohibited" in content:
            risk_implications.append("prohibited_practices")
        if "high-risk" in content:
            risk_implications.append("high_risk_systems")
        if "limited risk" in content:
            risk_implications.append("limited_risk_systems")
        if "minimal risk" in content:
            risk_implications.append("minimal_risk_systems")
            
        # Check for specific risk areas
        if "safety" in content or "security" in content:
            risk_implications.append("safety_security")
        if "privacy" in content or "data protection" in content:
            risk_implications.append("privacy_data_protection")
        if "transparency" in content or "explainability" in content:
            risk_implications.append("transparency_explainability")
        if "fairness" in content or "non-discrimination" in content:
            risk_implications.append("fairness_non_discrimination")
            
        return risk_implications
    
    def _format_sources_with_compliance_info(self, docs: List[Document]) -> List[Dict[str, Any]]:
        """Format sources with compliance-specific information."""
        sources = []
        
        for doc in docs:
            metadata = doc.metadata or {}
            
            source = {
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "source": metadata.get("source", "Unknown source"),
                "filename": metadata.get("filename", "Unknown file"),
                "similarity_score": metadata.get("similarity_score", 0.0),
                "compliance_relevance": metadata.get("compliance_relevance", "low"),
                "risk_implications": metadata.get("risk_implications", []),
                "risk_category": metadata.get("risk_category", "general"),
                "article_references": metadata.get("article_references", []),
                "compliance_keywords": metadata.get("compliance_keywords", [])
            }
            
            sources.append(source)
            
        return sources
    
    def get_compliance_insights(self, question: str) -> Dict[str, Any]:
        """Get compliance insights for a question."""
        # Retrieve documents
        docs = self._retrieve_documents(question, max_sources=10)
        
        # Analyze compliance aspects
        risk_categories = set()
        article_references = set()
        compliance_keywords = set()
        
        for doc in docs:
            metadata = doc.metadata or {}
            if 'risk_category' in metadata:
                risk_categories.add(metadata['risk_category'])
            if 'article_references' in metadata:
                article_references.update(metadata['article_references'])
            if 'compliance_keywords' in metadata:
                compliance_keywords.update(metadata['compliance_keywords'])
        
        return {
            "risk_categories": list(risk_categories),
            "article_references": list(article_references),
            "compliance_keywords": list(compliance_keywords),
            "total_documents": len(docs),
            "compliance_focus": True
        }
    
    async def answer_compliance_question_streaming(
        self, 
        question: str, 
        session_id: str,
        user_id: Optional[str] = None,
        request_id: str | None = None,
        max_sources: int = 5
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Answer compliance question with streaming response and conversation memory."""
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        # Get or create conversation memory
        memory = memory_manager.get_or_create_memory(session_id, user_id)
        
        # Start observability tracing
        with self.observability.trace_rag_pipeline(request_id, question) as span:
            try:
                # Yield initial metadata
                yield {
                    "type": "metadata",
                    "request_id": request_id,
                    "session_id": session_id,
                    "timestamp": span.start_time.isoformat(),
                    "has_conversation_history": len(memory.get_conversation_history()) > 0
                }
                
                # Get conversation context
                context_summary = memory.get_context_summary()
                yield {
                    "type": "context",
                    "context": context_summary
                }
                
                # Stream response using advanced LangChain
                full_answer = ""
                sources = []
                compliance_metadata = {}
                
                async for chunk in self.advanced_langchain.answer_question_streaming(
                    question=question,
                    request_id=request_id,
                    use_conversation=True,
                    max_sources=max_sources
                ):
                    if chunk.get("type") == "content":
                        full_answer += chunk["content"]
                        yield chunk
                    elif chunk.get("type") == "sources":
                        sources = chunk["sources"]
                        yield chunk
                    elif chunk.get("type") == "final":
                        compliance_metadata = chunk.get("compliance_metadata", {})
                        yield chunk
                
                # Add interaction to memory
                memory.add_interaction(
                    question=question,
                    answer=full_answer,
                    sources=sources,
                    compliance_metadata=compliance_metadata
                )
                
                # Yield memory update
                yield {
                    "type": "memory_update",
                    "memory_stats": memory.get_memory_stats(),
                    "session_id": session_id
                }
                
                # Record observability metrics
                self.observability.record_evaluation_metrics(
                    compliance_metadata.get("compliance_score", 0.0),
                    compliance_metadata.get("compliance_score", 0.0),
                    request_id
                )
                
            except Exception as e:
                self.logger.error(f"Error in streaming compliance answer: {e}")
                span.set_status("error", str(e))
                yield {
                    "type": "error",
                    "error": str(e),
                    "request_id": request_id
                }
    
    def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for a session."""
        memory = memory_manager.get_or_create_memory(session_id)
        return memory.get_context_summary()
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session."""
        memory = memory_manager.get_or_create_memory(session_id)
        memory.clear_memory("all")
    
    def get_conversation_summary(self, session_id: str) -> str:
        """Get conversation summary for a session."""
        memory = memory_manager.get_or_create_memory(session_id)
        return memory.get_conversation_summary()
    
    def export_conversation(self, session_id: str) -> Dict[str, Any]:
        """Export conversation data for analysis."""
        memory = memory_manager.get_or_create_memory(session_id)
        return memory.export_conversation()
