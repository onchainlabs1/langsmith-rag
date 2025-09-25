"""Mock LangChain RAG implementation for testing without API keys."""

import logging
from typing import List, Dict, Any
from datetime import datetime
import random


class MockLangChainRAG:
    """Mock LangChain RAG implementation for testing."""
    
    def __init__(self):
        """Initialize the mock RAG system."""
        self.logger = logging.getLogger(__name__)
        
        # Mock documents
        self.documents = [
            {
                "content": "Article 6 - Classification of AI systems as high-risk. AI systems shall be classified as high-risk where they are intended to be used as a safety component of a product, or the AI system is itself a product, covered by the Union harmonisation legislation listed in Annex II, or where the AI system is listed in Annex III.",
                "metadata": {"source": "eu_ai_act", "article": "Article 6", "topic": "high_risk_classification"}
            },
            {
                "content": "Article 7 - Conformity assessment procedures for high-risk AI systems. Before placing on the market or putting into service a high-risk AI system referred to in Article 6(2), the provider shall ensure that the system has been subject to a conformity assessment procedure in accordance with this Regulation.",
                "metadata": {"source": "eu_ai_act", "article": "Article 7", "topic": "conformity_assessment"}
            },
            {
                "content": "Article 8 - Obligations of providers of high-risk AI systems. Providers of high-risk AI systems shall ensure that their systems are designed and developed in accordance with the requirements set out in this Regulation. Providers shall implement appropriate risk management measures.",
                "metadata": {"source": "eu_ai_act", "article": "Article 8", "topic": "provider_obligations"}
            },
            {
                "content": "Article 13 - Transparency and provision of information to users. Providers and users of AI systems shall ensure that AI systems are designed and developed in such a way that natural persons are informed that they are interacting with an AI system.",
                "metadata": {"source": "eu_ai_act", "article": "Article 13", "topic": "transparency"}
            }
        ]
        
        self.initialized = False
        
    def setup_vectorstore(self, documents: List[str] = None, metadatas: List[Dict] = None):
        """Setup mock vector store."""
        self.initialized = True
        self.logger.info("Mock vector store initialized")
        return True
    
    def load_sample_documents(self):
        """Load sample documents."""
        return self.setup_vectorstore()
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using mock responses."""
        if not self.initialized:
            return {
                "answer": "Mock RAG system not initialized. Please call setup first.",
                "sources": [],
                "error": "Vector store not set up"
            }
        
        # Mock response based on question content
        question_lower = question.lower()
        
        if "high-risk" in question_lower or "high risk" in question_lower:
            answer = """Based on Article 6 of the EU AI Act, AI systems are classified as high-risk when they are:
            
1. Intended to be used as a safety component of a product, or
2. The AI system is itself a product, covered by the Union harmonisation legislation listed in Annex II, or
3. Listed in Annex III of the Regulation

High-risk AI systems are those that pose a high risk to the health and safety or fundamental rights of persons. These systems require strict conformity assessment procedures and compliance with specific obligations."""
            
            sources = [self.documents[0], self.documents[1]]
            
        elif "provider" in question_lower and "obligation" in question_lower:
            answer = """According to Article 8 of the EU AI Act, providers of high-risk AI systems have several key obligations:

1. Ensure systems are designed and developed in accordance with Regulation requirements
2. Implement appropriate risk management measures
3. Ensure AI systems are tested and validated before being placed on the market
4. Maintain documentation and records of the system's development and testing
5. Provide clear instructions for use and safety information

These obligations are essential for ensuring compliance and protecting users' rights."""
            
            sources = [self.documents[2]]
            
        elif "transparency" in question_lower:
            answer = """Under Article 13 of the EU AI Act, transparency requirements include:

1. Informing natural persons when they are interacting with an AI system (unless obvious from context)
2. Providing clear information about the AI system's capabilities and limitations
3. Ensuring users understand the system's purpose and functionality
4. Maintaining transparency in automated decision-making processes

These requirements are crucial for building trust and ensuring users can make informed decisions when interacting with AI systems."""
            
            sources = [self.documents[3]]
            
        else:
            answer = """Based on the EU AI Act provisions, I can provide information about:

1. High-risk AI system classification (Article 6)
2. Conformity assessment procedures (Article 7)
3. Provider obligations (Article 8)
4. Transparency requirements (Article 13)

Please ask a more specific question about any of these topics for detailed information."""
            
            sources = self.documents
        
        # Format sources
        formatted_sources = []
        for source in sources:
            formatted_sources.append({
                "content": source["content"],
                "metadata": source["metadata"],
                "source": source["metadata"]["source"],
                "article": source["metadata"]["article"]
            })
        
        return {
            "answer": answer,
            "sources": formatted_sources,
            "timestamp": datetime.now().isoformat(),
            "model": "mock-gpt-4",
            "temperature": 0.1
        }
    
    def get_similar_documents(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Get similar documents for a query."""
        if not self.initialized:
            return []
        
        query_lower = query.lower()
        scored_docs = []
        
        for doc in self.documents:
            score = 0
            content_lower = doc["content"].lower()
            
            # Simple scoring based on keyword matches
            if "high-risk" in query_lower and "high-risk" in content_lower:
                score += 0.9
            if "provider" in query_lower and "provider" in content_lower:
                score += 0.8
            if "transparency" in query_lower and "transparency" in content_lower:
                score += 0.8
            if "conformity" in query_lower and "conformity" in content_lower:
                score += 0.7
            
            # Add some randomness for variety
            score += random.random() * 0.1
            
            scored_docs.append((doc, score))
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        similar_docs = []
        for doc, score in scored_docs[:k]:
            similar_docs.append({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "source": doc["metadata"]["source"],
                "article": doc["metadata"]["article"],
                "score": score
            })
        
        return similar_docs
    
    def get_vectorstore_info(self) -> Dict[str, Any]:
        """Get information about the vector store."""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "total_documents": len(self.documents),
            "embedding_model": "mock-embeddings",
            "llm_model": "mock-gpt-4",
            "retriever_type": "similarity",
            "k_documents": 3
        }


# Global mock instance
mock_langchain_rag = MockLangChainRAG()
