"""Streaming API routes for EU AI Act Compliance RAG System."""

import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.app.services.rag_pipeline import ComplianceRAGPipeline
from src.services.vectorstore import VectorStoreService
from src.core.auth import get_current_user
from src.core.observability import get_observability_service


router = APIRouter(prefix="/v1/streaming", tags=["streaming"])
logger = logging.getLogger(__name__)


class StreamingQuestionRequest(BaseModel):
    """Request model for streaming questions."""
    question: str = Field(..., description="The compliance question to answer")
    session_id: str = Field(..., description="Session ID for conversation continuity")
    user_id: str = Field(None, description="User ID for personalization")
    max_sources: int = Field(5, description="Maximum number of sources to retrieve")


class ConversationContextResponse(BaseModel):
    """Response model for conversation context."""
    session_id: str
    context: dict
    memory_stats: dict


class ConversationClearRequest(BaseModel):
    """Request model for clearing conversation."""
    session_id: str


def get_rag_pipeline() -> ComplianceRAGPipeline:
    """Get RAG pipeline instance."""
    vectorstore_service = VectorStoreService()
    return ComplianceRAGPipeline(vectorstore_service)


async def generate_streaming_response(
    question: str,
    session_id: str,
    user_id: str = None,
    max_sources: int = 5
) -> AsyncGenerator[str, None]:
    """Generate streaming response for the question."""
    try:
        # Get RAG pipeline
        rag_pipeline = get_rag_pipeline()
        
        # Stream response
        async for chunk in rag_pipeline.answer_compliance_question_streaming(
            question=question,
            session_id=session_id,
            user_id=user_id,
            max_sources=max_sources
        ):
            # Format chunk as JSON with newline for SSE
            chunk_json = json.dumps(chunk, ensure_ascii=False)
            yield f"data: {chunk_json}\n\n"
        
        # Send end signal
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Error in streaming response: {e}")
        error_chunk = {
            "type": "error",
            "error": str(e),
            "timestamp": None
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"


@router.post("/ask")
async def ask_question_streaming(
    request: StreamingQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Ask a compliance question with streaming response.
    
    Returns a Server-Sent Events (SSE) stream with the following event types:
    - metadata: Initial metadata about the request
    - context: Conversation context and history
    - content: Streaming text content
    - sources: Retrieved source documents
    - memory_update: Memory statistics update
    - final: Final response with complete answer
    - error: Error information if something goes wrong
    """
    try:
        observability = get_observability_service()
        
        # Record request metrics
        observability.request_counter.add(1, {
            "method": "POST",
            "endpoint": "/v1/streaming/ask",
            "status_code": "200"
        })
        
        return StreamingResponse(
            generate_streaming_response(
                question=request.question,
                session_id=request.session_id,
                user_id=request.user_id,
                max_sources=request.max_sources
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming ask endpoint: {e}")
        observability.error_counter.add(1, {
            "error_type": type(e).__name__,
            "endpoint": "/v1/streaming/ask"
        })
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/{session_id}")
async def get_conversation_context(
    session_id: str,
    current_user: dict = Depends(get_current_user)
) -> ConversationContextResponse:
    """Get conversation context for a session."""
    try:
        rag_pipeline = get_rag_pipeline()
        context = rag_pipeline.get_conversation_context(session_id)
        
        return ConversationContextResponse(
            session_id=session_id,
            context=context,
            memory_stats=context.get("memory_stats", {})
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_conversation(
    request: ConversationClearRequest,
    current_user: dict = Depends(get_current_user)
):
    """Clear conversation history for a session."""
    try:
        rag_pipeline = get_rag_pipeline()
        rag_pipeline.clear_conversation(request.session_id)
        
        return {"message": "Conversation cleared successfully", "session_id": request.session_id}
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{session_id}")
async def get_conversation_summary(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get conversation summary for a session."""
    try:
        rag_pipeline = get_rag_pipeline()
        summary = rag_pipeline.get_conversation_summary(session_id)
        
        return {
            "session_id": session_id,
            "summary": summary,
            "timestamp": None
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{session_id}")
async def export_conversation(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Export conversation data for analysis."""
    try:
        rag_pipeline = get_rag_pipeline()
        export_data = rag_pipeline.export_conversation(session_id)
        
        return export_data
        
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for streaming endpoints."""
    return {
        "status": "healthy",
        "service": "streaming-api",
        "endpoints": [
            "POST /v1/streaming/ask",
            "GET /v1/streaming/context/{session_id}",
            "POST /v1/streaming/clear",
            "GET /v1/streaming/summary/{session_id}",
            "GET /v1/streaming/export/{session_id}"
        ]
    }
