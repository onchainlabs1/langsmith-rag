"""FastAPI application entry point."""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.api import router
from src.api.streaming_routes import router as streaming_router
from src.api.langchain_routes import router as langchain_router
from src.core import settings, setup_logging
from src.core.observability import setup_observability
from src.core.rate_limiter import rate_limit_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    setup_logging()
    setup_observability()
    
    # Initialize services
    from src.services.vectorstore import VectorStoreService
    from src.services.rag import RAGService
    
    # Load vectorstore
    vectorstore_service = VectorStoreService()
    try:
        vectorstore_service.load_vectorstore()
    except FileNotFoundError:
        # Initialize with AI Act corpus if vectorstore doesn't exist
        try:
            vectorstore_service.load_ai_act_corpus()
        except FileNotFoundError:
            # Fallback to general knowledge base
            vectorstore_service.load_knowledge_base()
    
    # Initialize RAG service
    rag_service = RAGService(vectorstore_service)
    
    # Store services in app state
    app.state.vectorstore_service = vectorstore_service
    app.state.rag_service = rag_service
    
    yield
    
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Include API routes
app.include_router(router)
app.include_router(streaming_router)
app.include_router(langchain_router)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.middleware("http")
async def add_request_id(request, call_next):
    """Add request ID to all requests."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
