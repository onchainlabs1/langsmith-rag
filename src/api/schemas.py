"""API request/response schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"


class AnswerRequest(BaseModel):
    """Answer request schema."""
    question: str = Field(..., description="The question to answer", min_length=1, max_length=1000)


class Source(BaseModel):
    """Source document schema."""
    content: str = Field(..., description="Relevant content from the source")
    source: str = Field(..., description="Source file path")
    filename: str = Field(..., description="Source filename")


class AnswerResponse(BaseModel):
    """Answer response schema."""
    answer: str = Field(..., description="The generated answer")
    sources: List[Source] = Field(..., description="Source documents used")
    trace_url: str = Field(..., description="LangSmith trace URL")
    request_id: str = Field(..., description="Request ID for tracking")


class EvaluationRequest(BaseModel):
    """Offline evaluation request schema."""
    dataset_path: str = Field(..., description="Path to evaluation dataset")
    output_dir: Optional[str] = Field(None, description="Output directory for results")


class EvaluationResult(BaseModel):
    """Evaluation result schema."""
    question: str
    reference: str
    answer: str
    sources: List[Source]
    groundedness_score: float
    correctness_score: float
    trace_url: str
    request_id: str


class EvaluationReport(BaseModel):
    """Evaluation report schema."""
    total_questions: int
    avg_groundedness: float
    avg_correctness: float
    passed_threshold: bool
    results: List[EvaluationResult]


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")
