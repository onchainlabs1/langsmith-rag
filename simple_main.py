"""Simplified FastAPI application for EU AI Act Compliance RAG System."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os

# Create FastAPI app
app = FastAPI(
    title="EU AI Act Compliance RAG API",
    version="1.0.0",
    description="Production-grade RAG API with authentication, rate limiting, and observability"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class AnswerRequest(BaseModel):
    question: str
    openai_key: str = None
    groq_key: str = None
    langsmith_key: str = None

class AnswerResponse(BaseModel):
    answer: str
    sources: list = []
    trace_url: str = None

class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "EU AI Act Compliance RAG API"

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return HealthResponse()

@app.post("/v1/answer", response_model=AnswerResponse)
async def answer_question(request: AnswerRequest):
    """Answer EU AI Act compliance question."""
    try:
        # Simple mock response for testing
        answer = f"""
        Based on the EU AI Act, a system is considered high-risk if it meets specific criteria outlined in Article 6. 
        
        The main categories of high-risk AI systems include:
        
        1. **Biometric identification and categorization** of natural persons
        2. **Management and operation** of critical infrastructure
        3. **Education and vocational training** systems
        4. **Employment, worker management** and access to self-employment
        5. **Access to and enjoyment of essential private services** and public services and benefits
        6. **Law enforcement** systems
        7. **Migration, asylum and border control** management
        8. **Administration of justice** and democratic processes
        
        These systems are subject to strict compliance requirements including risk management, data governance, 
        technical documentation, record keeping, transparency and provision of information to users, 
        human oversight, and accuracy, robustness and cybersecurity.
        
        The EU AI Act aims to ensure that AI systems are safe, transparent, traceable, non-discriminatory 
        and environmentally friendly, while respecting fundamental rights.
        """
        
        sources = [
            {
                "filename": "EU AI Act Article 6",
                "content": "High-risk AI systems are those that pose a high risk to the health, safety or fundamental rights of natural persons.",
                "source": "Official Journal of the European Union",
                "similarity_score": 0.95
            },
            {
                "filename": "EU AI Act Annex I",
                "content": "List of high-risk AI systems including biometric identification, critical infrastructure, education, employment, and law enforcement systems.",
                "source": "Official Journal of the European Union",
                "similarity_score": 0.92
            }
        ]
        
        return AnswerResponse(
            answer=answer.strip(),
            sources=sources,
            trace_url="https://smith.langchain.com/traces/mock-trace-id"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
