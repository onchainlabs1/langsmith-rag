"""API route handlers."""

import logging
import uuid
import time
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends, Request
from langsmith import Client

from src.api.schemas import (
    HealthResponse, 
    AnswerRequest, 
    AnswerResponse, 
    EvaluationRequest,
    EvaluationReport,
    LoginRequest,
    LoginResponse
)
from src.services.rag import RAGService
from src.services.vectorstore import VectorStoreService
from src.evals.evaluators import EvaluationService
from src.app.services.rag_pipeline import ComplianceRAGPipeline
from src.core.auth import (
    auth_service, 
    get_current_user, 
    require_read, 
    require_evaluate,
    User
)
from src.core.rate_limiter import rate_limit_middleware
from src.core.observability import get_observability_service

# Create router
router = APIRouter()

# Global services (in production, use dependency injection)
_vectorstore_service: VectorStoreService | None = None
_rag_service: RAGService | None = None
_evaluation_service: EvaluationService | None = None
_compliance_rag_pipeline: ComplianceRAGPipeline | None = None


def get_vectorstore_service() -> VectorStoreService:
    """Get vectorstore service instance."""
    global _vectorstore_service
    if _vectorstore_service is None:
        _vectorstore_service = VectorStoreService()
        try:
            _vectorstore_service.load_vectorstore()
        except FileNotFoundError:
            # Initialize with knowledge base if vectorstore doesn't exist
            _vectorstore_service.load_knowledge_base()
    return _vectorstore_service


def get_rag_service() -> RAGService:
    """Get RAG service instance."""
    global _rag_service
    if _rag_service is None:
        vectorstore_service = get_vectorstore_service()
        _rag_service = RAGService(vectorstore_service)
    return _rag_service


def get_evaluation_service() -> EvaluationService:
    """Get evaluation service instance."""
    global _evaluation_service
    if _evaluation_service is None:
        rag_service = get_rag_service()
        _evaluation_service = EvaluationService(rag_service)
    return _evaluation_service


def get_compliance_rag_pipeline() -> ComplianceRAGPipeline:
    """Get compliance RAG pipeline instance."""
    global _compliance_rag_pipeline
    if _compliance_rag_pipeline is None:
        vectorstore_service = get_vectorstore_service()
        _compliance_rag_pipeline = ComplianceRAGPipeline(vectorstore_service)
    return _compliance_rag_pipeline


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse()


@router.post("/v1/answer", response_model=AnswerResponse)
async def answer_question(
    request: AnswerRequest,
    current_user: User = Depends(require_read),
    compliance_pipeline: ComplianceRAGPipeline = Depends(get_compliance_rag_pipeline),
    http_request: Request = None
) -> AnswerResponse:
    """Answer EU AI Act compliance question using specialized RAG pipeline."""
    from src.core.security import input_validator, rate_limiter, security_headers
    
    # Get client IP for rate limiting
    client_ip = http_request.client.host if http_request else "unknown"
    
    # Check rate limiting
    rate_limit_result = rate_limiter.check_rate_limit(client_ip, current_user.user_id)
    if not rate_limit_result["allowed"]:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {rate_limit_result['reason']}",
            headers={"Retry-After": str(rate_limit_result.get("retry_after", 60))}
        )
    
    # Validate and sanitize input
    validation_result = input_validator.validate_question(request.question)
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {'; '.join(validation_result['errors'])}"
        )
    
    # Use sanitized question
    sanitized_question = validation_result["sanitized"]
    
    observability = get_observability_service()
    request_id = str(uuid.uuid4())
    
    with observability.trace_rag_pipeline(request_id, sanitized_question):
        try:
            # Log request with user context (sanitized)
            logger = logging.getLogger(__name__)
            safe_question = input_validator.sanitize_for_logging(sanitized_question)
            logger.info(
                "Processing EU AI Act compliance question",
                extra={
                    "request_id": request_id,
                    "user_id": current_user.user_id,
                    "question": safe_question,
                    "compliance_focus": True,
                    "warnings": validation_result.get("warnings", [])
                }
            )
            
            # Get compliance-focused answer
            result = compliance_pipeline.answer_compliance_question(request.question, request_id)
            
            # Record metrics
            if "compliance_metadata" in result:
                metadata = result["compliance_metadata"]
                if "validation" in metadata:
                    validation = metadata["validation"]
                    if "confidence_score" in validation:
                        observability.record_groundedness(validation["confidence_score"], request_id)
            
            return AnswerResponse(**result)
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(
                "Error processing compliance question",
                extra={
                    "request_id": request_id,
                    "user_id": current_user.user_id,
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=500, detail=f"Error processing compliance question: {str(e)}")


@router.post("/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Authenticate user and return JWT token."""
    try:
        # Authenticate user (simplified for demo)
        user = auth_service.authenticate_user(request.username, request.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Create JWT token
        token = auth_service.create_access_token(user)
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.user_id,
            username=user.username,
            role=user.role.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/v1/evaluate/offline", response_model=EvaluationReport)
async def run_offline_evaluation(
    request: EvaluationRequest,
    current_user: User = Depends(require_evaluate),
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
) -> EvaluationReport:
    """Run offline evaluation on a dataset (requires analyst or admin role)."""
    try:
        logger = logging.getLogger(__name__)
        logger.info(
            "Running offline evaluation",
            extra={
                "user_id": current_user.user_id,
                "dataset_path": request.dataset_path,
                "output_dir": request.output_dir
            }
        )
        
        report = evaluation_service.run_evaluation(
            dataset_path=request.dataset_path,
            output_dir=request.output_dir
        )
        return report
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error running evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running evaluation: {str(e)}")
