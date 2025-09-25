"""LangChain RAG API routes."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.services.langchain_rag import langchain_rag
from src.services.mock_langchain_rag import mock_langchain_rag
from src.services.groq_langchain_rag import groq_langchain_rag
from src.core.auth import get_current_user
import os

router = APIRouter(prefix="/v1/langchain", tags=["langchain"])
logger = logging.getLogger(__name__)


class QuestionRequest(BaseModel):
    """Request model for questions."""
    question: str


class AnswerResponse(BaseModel):
    """Response model for answers."""
    answer: str
    sources: list
    timestamp: str
    model: str
    temperature: float


class VectorStoreInfo(BaseModel):
    """Vector store information."""
    status: str
    total_documents: int = 0
    embedding_model: str = ""
    llm_model: str = ""
    retriever_type: str = ""
    k_documents: int = 0


def get_rag_system():
    """Get the appropriate RAG system based on API key availability."""
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Priority: Groq > OpenAI > Mock
    if groq_key and not groq_key.startswith("gsk_test"):
        return groq_langchain_rag
    elif openai_key and not openai_key.startswith("sk-test"):
        return langchain_rag
    else:
        return mock_langchain_rag


@router.post("/setup", response_model=Dict[str, str])
async def setup_rag_system(current_user: dict = Depends(get_current_user)):
    """Setup the LangChain RAG system with sample documents."""
    try:
        rag_system = get_rag_system()
        success = rag_system.load_sample_documents()
        
        if success:
            if rag_system == groq_langchain_rag:
                system_type = "Groq + LangChain"
            elif rag_system == langchain_rag:
                system_type = "OpenAI + LangChain"
            else:
                system_type = "Mock"
            
            return {
                "status": "success", 
                "message": f"RAG system initialized with sample EU AI Act documents using {system_type} implementation",
                "system_type": system_type,
                "llm_provider": getattr(rag_system, 'llm', {}).get('model_name', 'unknown') if hasattr(rag_system, 'llm') else 'mock'
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize RAG system")
            
    except Exception as e:
        logger.error(f"Error setting up RAG system: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Ask a question using the LangChain RAG system."""
    try:
        rag_system = get_rag_system()
        result = rag_system.answer_question(request.question)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnswerResponse(
            answer=result["answer"],
            sources=result["sources"],
            timestamp=result["timestamp"],
            model=result["model"],
            temperature=result["temperature"]
        )
        
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{query}")
async def get_similar_documents(
    query: str,
    k: int = 3,
    current_user: dict = Depends(get_current_user)
):
    """Get similar documents for a query."""
    try:
        rag_system = get_rag_system()
        docs = rag_system.get_similar_documents(query, k)
        return {
            "query": query,
            "documents": docs,
            "count": len(docs)
        }
        
    except Exception as e:
        logger.error(f"Error getting similar documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info", response_model=VectorStoreInfo)
async def get_vectorstore_info(current_user: dict = Depends(get_current_user)):
    """Get information about the vector store."""
    try:
        rag_system = get_rag_system()
        info = rag_system.get_vectorstore_info()
        return VectorStoreInfo(**info)
        
    except Exception as e:
        logger.error(f"Error getting vector store info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for LangChain endpoints."""
    return {
        "status": "healthy",
        "service": "langchain-rag",
        "endpoints": [
            "POST /v1/langchain/setup",
            "POST /v1/langchain/ask",
            "GET /v1/langchain/similar/{query}",
            "GET /v1/langchain/info"
        ]
    }
