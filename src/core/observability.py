"""OpenTelemetry observability for EU AI Act Compliance RAG System."""

import logging
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode
from opentelemetry.metrics import Counter, Histogram, UpDownCounter

from src.core.config import settings


class ObservabilityService:
    """Observability service for tracing, metrics, and logging."""
    
    def __init__(self) -> None:
        """Initialize observability service."""
        self.tracer = trace.get_tracer(__name__)
        self.meter = metrics.get_meter(__name__)
        
        # Custom metrics
        self.request_counter = self.meter.create_counter(
            name="rag_requests_total",
            description="Total number of RAG requests",
            unit="1"
        )
        
        self.request_duration = self.meter.create_histogram(
            name="rag_request_duration_seconds",
            description="Duration of RAG requests in seconds",
            unit="s"
        )
        
        self.retrieval_duration = self.meter.create_histogram(
            name="rag_retrieval_duration_seconds", 
            description="Duration of document retrieval in seconds",
            unit="s"
        )
        
        self.llm_duration = self.meter.create_histogram(
            name="rag_llm_duration_seconds",
            description="Duration of LLM calls in seconds", 
            unit="s"
        )
        
        self.groundedness_score = self.meter.create_histogram(
            name="rag_groundedness_score",
            description="Groundedness scores for RAG responses",
            unit="1"
        )
        
        self.correctness_score = self.meter.create_histogram(
            name="rag_correctness_score", 
            description="Correctness scores for RAG responses",
            unit="1"
        )
        
        self.retrieval_k = self.meter.create_histogram(
            name="rag_retrieval_k",
            description="Number of documents retrieved",
            unit="1"
        )
        
        self.active_requests = self.meter.create_up_down_counter(
            name="rag_active_requests",
            description="Number of active RAG requests",
            unit="1"
        )
        
        self.error_counter = self.meter.create_counter(
            name="rag_errors_total",
            description="Total number of RAG errors",
            unit="1"
        )
        
    def setup_tracing(self) -> None:
        """Setup OpenTelemetry tracing."""
        # Create resource
        resource = Resource.create({
            "service.name": "eu-ai-act-rag-api",
            "service.version": "1.0.0",
            "deployment.environment": settings.environment
        })
        
        # Setup tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer_provider = trace.get_tracer_provider()
        
        # Add OTLP exporter if configured
        if settings.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
        
        # Setup FastAPI instrumentation
        FastAPIInstrumentor.instrument_app = self._instrument_fastapi
        
    def setup_metrics(self) -> None:
        """Setup OpenTelemetry metrics."""
        # Create resource
        resource = Resource.create({
            "service.name": "eu-ai-act-rag-api",
            "service.version": "1.0.0",
            "deployment.environment": settings.environment
        })
        
        # Setup meter provider
        readers = []
        
        # Add Prometheus reader
        prometheus_reader = PrometheusMetricReader()
        readers.append(prometheus_reader)
        
        # Add OTLP reader if configured
        if settings.otlp_endpoint:
            otlp_exporter = OTLPMetricExporter(endpoint=settings.otlp_endpoint)
            otlp_reader = PeriodicExportingMetricReader(otlp_exporter)
            readers.append(otlp_reader)
        
        meter_provider = MeterProvider(resource=resource, metric_readers=readers)
        metrics.set_meter_provider(meter_provider)
        
    def _instrument_fastapi(self, app):
        """Instrument FastAPI app with custom middleware."""
        FastAPIInstrumentor.instrument_app(app)
        
        # Add custom middleware for RAG-specific metrics
        @app.middleware("http")
        async def observability_middleware(request, call_next):
            start_time = time.time()
            
            # Increment active requests
            self.active_requests.add(1)
            
            try:
                response = await call_next(request)
                
                # Record metrics
                duration = time.time() - start_time
                self.request_duration.record(duration)
                
                # Record request counter with labels
                self.request_counter.add(1, {
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": str(response.status_code)
                })
                
                return response
                
            except Exception as e:
                # Record error
                self.error_counter.add(1, {
                    "error_type": type(e).__name__,
                    "endpoint": request.url.path
                })
                raise
            finally:
                # Decrement active requests
                self.active_requests.add(-1)
    
    @contextmanager
    def trace_rag_pipeline(self, request_id: str, question: str):
        """Context manager for tracing RAG pipeline."""
        with self.tracer.start_as_current_span("rag_pipeline") as span:
            span.set_attributes({
                "request_id": request_id,
                "question": question[:100],  # Truncate for privacy
                "pipeline": "compliance_rag"
            })
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    @contextmanager
    def trace_retrieval(self, query: str, k: int):
        """Context manager for tracing document retrieval."""
        with self.tracer.start_as_current_span("document_retrieval") as span:
            span.set_attributes({
                "query": query[:100],
                "retrieval_k": k
            })
            
            start_time = time.time()
            try:
                yield span
            finally:
                duration = time.time() - start_time
                self.retrieval_duration.record(duration)
                self.retrieval_k.record(k)
    
    @contextmanager
    def trace_llm_call(self, model: str, prompt_length: int):
        """Context manager for tracing LLM calls."""
        with self.tracer.start_as_current_span("llm_call") as span:
            span.set_attributes({
                "model": model,
                "prompt_length": prompt_length
            })
            
            start_time = time.time()
            try:
                yield span
            finally:
                duration = time.time() - start_time
                self.llm_duration.record(duration)
    
    def record_groundedness(self, score: float, request_id: str):
        """Record groundedness score."""
        self.groundedness_score.record(score, {
            "request_id": request_id
        })
    
    def record_correctness(self, score: float, request_id: str):
        """Record correctness score."""
        self.correctness_score.record(score, {
            "request_id": request_id
        })
    
    def record_evaluation_metrics(self, groundedness: float, correctness: float, request_id: str):
        """Record evaluation metrics."""
        self.record_groundedness(groundedness, request_id)
        self.record_correctness(correctness, request_id)
    
    def setup_logging(self) -> None:
        """Setup structured logging."""
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add custom log formatter for structured logs
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                
                # Add request context if available
                if hasattr(record, "request_id"):
                    log_entry["request_id"] = record.request_id
                if hasattr(record, "user_id"):
                    log_entry["user_id"] = record.user_id
                if hasattr(record, "duration"):
                    log_entry["duration"] = record.duration
                    
                return str(log_entry)
        
        # Apply formatter to all handlers
        for handler in logging.getLogger().handlers:
            handler.setFormatter(StructuredFormatter())


# Global observability service
observability = ObservabilityService()


def setup_observability() -> None:
    """Setup complete observability stack."""
    observability.setup_tracing()
    observability.setup_metrics()
    observability.setup_logging()
    
    # Instrument HTTP clients
    RequestsInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()


def get_observability_service() -> ObservabilityService:
    """Get observability service instance."""
    return observability
