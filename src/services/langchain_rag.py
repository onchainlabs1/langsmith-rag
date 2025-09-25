"""Simple and functional LangChain RAG implementation."""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import BaseRetriever

from src.core.config import settings
from src.services.vectorstore import VectorStoreService


class SimpleLangChainRAG:
    """Simple and functional LangChain RAG implementation."""
    
    def __init__(self):
        """Initialize the LangChain RAG system."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            max_tokens=1000,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize embeddings
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
        
        # Initialize prompt template
        self.prompt_template = PromptTemplate(
            template="""You are an expert on EU AI Act compliance. Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            
            Provide a comprehensive answer focusing on:
            1. The specific EU AI Act requirements
            2. Risk categories and implications
            3. Compliance obligations
            4. Practical guidance for implementation

            Context:
            {context}

            Question: {question}
            
            Answer:""",
            input_variables=["context", "question"]
        )
        
    def setup_vectorstore(self, documents: List[str], metadatas: List[Dict] = None):
        """Setup vector store with documents."""
        try:
            self.logger.info("Setting up vector store...")
            
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
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": self.prompt_template}
            )
            
            self.logger.info(f"Vector store setup complete with {len(texts)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up vector store: {e}")
            return False
    
    def load_sample_documents(self):
        """Load sample EU AI Act documents for testing."""
        sample_docs = [
            """Article 6 - Classification of AI systems as high-risk
            AI systems shall be classified as high-risk where they are intended to be used as a safety component of a product, or the AI system is itself a product, covered by the Union harmonisation legislation listed in Annex II, or where the AI system is listed in Annex III.

            The AI systems referred to in paragraph 1 shall be considered high-risk if they pose a high risk to the health and safety or fundamental rights of persons.""",
            
            """Article 7 - Conformity assessment procedures for high-risk AI systems
            Before placing on the market or putting into service a high-risk AI system referred to in Article 6(2), the provider shall ensure that the system has been subject to a conformity assessment procedure in accordance with this Regulation.

            The conformity assessment procedure shall be carried out by the provider itself or by a notified body.""",
            
            """Article 8 - Obligations of providers of high-risk AI systems
            Providers of high-risk AI systems shall ensure that their systems are designed and developed in accordance with the requirements set out in this Regulation.

            Providers shall implement appropriate risk management measures and ensure that the AI system is tested and validated before being placed on the market or put into service.""",
            
            """Article 13 - Transparency and provision of information to users
            Providers and users of AI systems shall ensure that AI systems are designed and developed in such a way that natural persons are informed that they are interacting with an AI system.

            This obligation shall apply to AI systems that interact with natural persons, unless this is obvious from the circumstances and the context of use."""
        ]
        
        metadatas = [
            {"source": "eu_ai_act", "article": "Article 6", "topic": "high_risk_classification"},
            {"source": "eu_ai_act", "article": "Article 7", "topic": "conformity_assessment"},
            {"source": "eu_ai_act", "article": "Article 8", "topic": "provider_obligations"},
            {"source": "eu_ai_act", "article": "Article 13", "topic": "transparency"}
        ]
        
        return self.setup_vectorstore(sample_docs, metadatas)
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using the RAG system."""
        if not self.qa_chain:
            return {
                "answer": "RAG system not initialized. Please load documents first.",
                "sources": [],
                "error": "Vector store not set up"
            }
        
        try:
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            # Extract answer and sources
            answer = result["result"]
            source_docs = result["source_documents"]
            
            # Format sources
            sources = []
            for doc in source_docs:
                sources.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "unknown"),
                    "article": doc.metadata.get("article", "unknown")
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "model": self.llm.model_name,
                "temperature": self.llm.temperature
            }
            
        except Exception as e:
            self.logger.error(f"Error answering question: {e}")
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
                    "article": doc.metadata.get("article", "unknown")
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
                "embedding_model": "text-embedding-ada-002",
                "llm_model": self.llm.model_name,
                "retriever_type": "similarity",
                "k_documents": 5
            }
            
        except Exception as e:
            self.logger.error(f"Error getting vector store info: {e}")
            return {"status": "error", "error": str(e)}


# Global instance
langchain_rag = SimpleLangChainRAG()
