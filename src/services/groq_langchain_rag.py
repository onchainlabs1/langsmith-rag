"""Groq-based LangChain RAG implementation for EU AI Act Compliance."""

import os
import logging
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langsmith import Client

from src.core.config import settings


class GroqLangChainRAG:
    """Groq-based LangChain RAG implementation."""
    
    def __init__(self):
        """Initialize the Groq LangChain RAG system."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-70b-versatile",  # Fast and capable model
            temperature=0.1,
            max_tokens=1000
        )
        
        # Initialize embeddings (still using OpenAI for embeddings as Groq doesn't provide them)
        self.embeddings = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Vector store
        self.vectorstore = None
        self.retriever = None
        
        # RAG chain
        self.qa_chain = None
        
        # Initialize LangSmith client
        self.langsmith_client = Client(
            api_key=os.getenv("LANGCHAIN_API_KEY")
        )
        
        # Initialize prompt template for EU AI Act compliance
        self.prompt_template = PromptTemplate(
            template="""You are an expert on EU AI Act compliance. Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            
            Provide a comprehensive answer focusing on:
            1. The specific EU AI Act requirements and articles
            2. Risk categories and their implications
            3. Compliance obligations for providers and users
            4. Practical guidance for implementation
            5. Relevant penalties and enforcement measures

            Context:
            {context}

            Question: {question}
            
            Answer:""",
            input_variables=["context", "question"]
        )
        
    def setup_vectorstore(self, documents: List[str], metadatas: List[Dict] = None):
        """Setup vector store with documents."""
        try:
            self.logger.info("Setting up vector store with Groq LLM...")
            
            # Split documents
            texts = self.text_splitter.split_text("\n\n".join(documents))
            
            # Prepare metadata
            if metadatas is None:
                metadatas = [{"source": f"doc_{i}"} for i in range(len(texts))]
            
            # Create vector store
            self.vectorstore = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            
            # Create retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            # Create QA chain with Groq
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": self.prompt_template}
            )
            
            self.logger.info(f"Vector store setup complete with {len(texts)} documents using Groq LLM")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up vector store: {e}")
            return False
    
    def load_sample_documents(self):
        """Load sample EU AI Act documents for testing."""
        sample_docs = [
            """Article 6 - Classification of AI systems as high-risk
            AI systems shall be classified as high-risk where they are intended to be used as a safety component of a product, or the AI system is itself a product, covered by the Union harmonisation legislation listed in Annex II, or where the AI system is listed in Annex III.

            The AI systems referred to in paragraph 1 shall be considered high-risk if they pose a high risk to the health and safety or fundamental rights of persons.

            High-risk AI systems include but are not limited to:
            - AI systems used in critical infrastructure
            - AI systems used in education and vocational training
            - AI systems used in employment and worker management
            - AI systems used in essential private and public services
            - AI systems used in law enforcement
            - AI systems used in migration, asylum and border control management
            - AI systems used in the administration of justice and democratic processes""",
            
            """Article 7 - Conformity assessment procedures for high-risk AI systems
            Before placing on the market or putting into service a high-risk AI system referred to in Article 6(2), the provider shall ensure that the system has been subject to a conformity assessment procedure in accordance with this Regulation.

            The conformity assessment procedure shall be carried out by the provider itself or by a notified body.

            The conformity assessment procedure shall include:
            - Risk management system assessment
            - Data governance and management practices review
            - Technical documentation evaluation
            - Quality management system audit
            - Post-market monitoring system verification""",
            
            """Article 8 - Obligations of providers of high-risk AI systems
            Providers of high-risk AI systems shall ensure that their systems are designed and developed in accordance with the requirements set out in this Regulation.

            Providers shall implement appropriate risk management measures and ensure that the AI system is tested and validated before being placed on the market or put into service.

            Key obligations include:
            - Establish and maintain a risk management system
            - Implement data governance and management practices
            - Prepare technical documentation
            - Maintain logs of the AI system's operation
            - Ensure human oversight
            - Provide information and instructions for use
            - Implement quality management system""",
            
            """Article 13 - Transparency and provision of information to users
            Providers and users of AI systems shall ensure that AI systems are designed and developed in such a way that natural persons are informed that they are interacting with an AI system.

            This obligation shall apply to AI systems that interact with natural persons, unless this is obvious from the circumstances and the context of use.

            Transparency requirements include:
            - Clear identification of AI systems
            - Information about the system's capabilities and limitations
            - Explanation of the system's purpose and functionality
            - Disclosure of automated decision-making processes
            - Information about data processing and storage""",
            
            """Article 71 - Penalties and enforcement
            Member States shall lay down the rules on penalties applicable to infringements of this Regulation and shall take all measures necessary to ensure that they are implemented.

            The penalties provided for shall be effective, proportionate and dissuasive.

            Penalties may include:
            - Administrative fines up to €30,000,000 or 6% of total worldwide annual turnover
            - Temporary or permanent prohibition of AI system deployment
            - Withdrawal of AI systems from the market
            - Publication of non-compliance decisions
            - Corrective measures and compliance orders"""
        ]
        
        metadatas = [
            {"source": "eu_ai_act", "article": "Article 6", "topic": "high_risk_classification", "compliance_level": "critical"},
            {"source": "eu_ai_act", "article": "Article 7", "topic": "conformity_assessment", "compliance_level": "critical"},
            {"source": "eu_ai_act", "article": "Article 8", "topic": "provider_obligations", "compliance_level": "critical"},
            {"source": "eu_ai_act", "article": "Article 13", "topic": "transparency", "compliance_level": "high"},
            {"source": "eu_ai_act", "article": "Article 71", "topic": "penalties", "compliance_level": "critical"}
        ]
        
        return self.setup_vectorstore(sample_docs, metadatas)
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using the Groq RAG system with LangSmith tracing."""
        if not self.qa_chain:
            return {
                "answer": "RAG system not initialized. Please load documents first.",
                "sources": [],
                "error": "Vector store not set up"
            }
        
        try:
            # Generate correlation ID for tracing
            correlation_id = request_id or str(uuid.uuid4())
            start_time = time.time()
            
            # Get answer from QA chain (tracing is automatic via environment variables)
            result = self.qa_chain({"query": question})
            
            # Extract answer and sources
            answer = result["result"]
            source_docs = result["source_documents"]
            
            # Calculate metrics
            total_duration = time.time() - start_time
            input_tokens = len(question.split()) * 1.3  # Rough estimation
            output_tokens = len(answer.split()) * 1.3  # Rough estimation
            cost = (input_tokens * 0.0005 + output_tokens * 0.0015) / 1000  # Approximate cost
            
            # Format sources
            sources = []
            citations_count = 0
            for doc in source_docs:
                sources.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "unknown"),
                    "article": doc.metadata.get("article", "unknown"),
                    "topic": doc.metadata.get("topic", "unknown"),
                    "compliance_level": doc.metadata.get("compliance_level", "medium")
                })
                citations_count += 1
            
            # Calculate citation validity (simple heuristic)
            citation_validity = min(1.0, citations_count / 3.0)  # Assume 3 citations is ideal
            
            # Record observability metrics
            if hasattr(self, 'observability'):
                self.observability.record_request_metrics(
                    correlation_id=correlation_id,
                    provider="groq",
                    input_tokens=int(input_tokens),
                    output_tokens=int(output_tokens),
                    cost=cost
                )
                self.observability.record_citation_metrics(
                    citations_count=citations_count,
                    validity_score=citation_validity,
                    correlation_id=correlation_id
                )
            
            return {
                "answer": answer,
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "model": "llama-3.1-70b-versatile",
                "provider": "groq",
                "temperature": self.llm.temperature,
                "trace_url": "https://smith.langchain.com/trace/auto-generated",
                "metadata": {
                    "correlation_id": correlation_id,
                    "total_duration": total_duration,
                    "input_tokens": int(input_tokens),
                    "output_tokens": int(output_tokens),
                    "estimated_cost": cost,
                    "citations_count": citations_count,
                    "citation_validity": citation_validity,
                    "retriever_type": "faiss",
                    "fallback_used": False
                }
            }
                
        except Exception as e:
            self.logger.error(f"Error answering question with Groq: {e}")
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def get_similar_documents(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Get similar documents for a query."""
        if not self.retriever:
            return []
        
        try:
            docs = self.retriever.get_relevant_documents(query)
            
            similar_docs = []
            for doc in docs[:k]:
                similar_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "unknown"),
                    "article": doc.metadata.get("article", "unknown"),
                    "topic": doc.metadata.get("topic", "unknown"),
                    "compliance_level": doc.metadata.get("compliance_level", "medium")
                })
            
            return similar_docs
            
        except Exception as e:
            self.logger.error(f"Error getting similar documents: {e}")
            return []
    
    def get_vectorstore_info(self) -> Dict[str, Any]:
        """Get information about the vector store."""
        if not self.vectorstore:
            return {"status": "not_initialized"}
        
        try:
            # Get total number of documents
            total_docs = self.vectorstore.index.ntotal
            
            return {
                "status": "initialized",
                "total_documents": total_docs,
                "embedding_model": "text-embedding-ada-002",  # OpenAI embeddings
                "llm_model": "llama-3.1-70b-versatile",
                "llm_provider": "groq",
                "retriever_type": "similarity",
                "k_documents": 5,
                "langsmith_enabled": True
            }
            
        except Exception as e:
            self.logger.error(f"Error getting vector store info: {e}")
            return {"status": "error", "error": str(e)}


# Global instance
groq_langchain_rag = GroqLangChainRAG()
