# 🚀 LangSmith RAG System

> **Status: 🚧 In Development** - A comprehensive RAG (Retrieval-Augmented Generation) system with full observability, evaluation, and monitoring capabilities.

## 📋 Overview

This project implements a production-ready RAG system using LangChain, LangSmith, and Groq, featuring comprehensive observability with Prometheus metrics, Grafana dashboards, and automated evaluation pipelines.

## ✨ Features

### 🔍 **Core RAG Capabilities**
- **Multi-Provider LLM Support**: OpenAI and Groq integration
- **Vector Search**: FAISS-based document retrieval
- **Conversation Memory**: Multiple memory types (Buffer, Summary, Entity, Knowledge Graph)
- **Streaming Responses**: Real-time response streaming
- **Document Processing**: PDF, TXT, and web content ingestion

### 📊 **Observability & Monitoring**
- **Prometheus Metrics**: Request rate, latency, error rates, token usage, costs
- **Grafana Dashboards**: Real-time visualization of system performance
- **OpenTelemetry Tracing**: Distributed tracing with LangSmith integration
- **Custom Metrics**: Citation validity, accuracy scores, fallback usage

### 🧪 **Evaluation & Testing**
- **LangSmith Evaluations**: Built-in and custom evaluators
- **Automated Testing**: Comprehensive test suite with CI/CD
- **Performance Benchmarks**: Latency, accuracy, and cost tracking
- **A/B Testing**: Compare different configurations

### 🔄 **Production Features**
- **Docker Support**: Containerized deployment
- **CI/CD Pipeline**: GitHub Actions with automated testing
- **Security**: JWT authentication, rate limiting, audit logs
- **Scalability**: Horizontal scaling with load balancing

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI API   │    │   LangSmith     │
│                 │◄──►│                 │◄──►│   Tracing       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │   RAG Engine    │    │   Vector Store  │
│   Metrics       │◄───│   (LangChain)   │◄──►│   (FAISS)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Grafana       │    │   Evaluation    │    │   Memory        │
│   Dashboards    │    │   Pipeline      │    │   Management    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key
- Groq API Key (optional)
- LangSmith API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fabio/langsmith-rag.git
   cd langsmith-rag
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start the monitoring stack**
   ```bash
   docker compose -f docker-compose-local.yml up -d
   ```

5. **Start the RAG API**
   ```bash
   python3 rag_mock_api.py
   ```

6. **Access the applications**
   - **Streamlit UI**: http://localhost:8501
   - **FastAPI**: http://localhost:8000
   - **Grafana**: http://localhost:3000 (admin/admin)
   - **Prometheus**: http://localhost:9090

## 📊 Monitoring & Observability

### Grafana Dashboards

Access real-time dashboards at http://localhost:3000:

- **RAG System Overview**: Request rates, response times, error rates
- **Token Usage**: Input/output token consumption
- **Cost Tracking**: Real-time cost monitoring
- **Accuracy Metrics**: Citation validity and response quality
- **System Health**: Service status and performance

### Prometheus Metrics

Available metrics at http://localhost:9090:

- `rag_requests_total`: Total requests by status
- `rag_request_duration_seconds`: Request latency by stage
- `rag_tokens_total`: Token usage by type
- `rag_cost_usd_total`: Cumulative costs
- `rag_accuracy_score`: Response accuracy (0-1)
- `rag_citations_per_response`: Citation count distribution

## 🧪 Evaluation

### Running Evaluations

```bash
# Run LangSmith evaluations
python3 evals/run_eval.py

# Run system tests
python3 test_full_system.py

# Generate test metrics
python3 generate_test_metrics.py
```

### Custom Evaluators

- **Citation Coverage**: Measures citation completeness
- **Regulatory Scope Match**: EU AI Act compliance
- **Faithfulness**: Response accuracy to source documents
- **Correctness**: Factual accuracy
- **Helpfulness**: User satisfaction metrics

## 🔧 Configuration

### Environment Variables

```bash
# LLM Providers
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key

# LangSmith
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=ai-act-rag

# Monitoring
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
```

### Docker Configuration

```yaml
# docker-compose-local.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus-local.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 📁 Project Structure

```
langsmith-rag/
├── src/                          # Source code
│   ├── api/                      # FastAPI routes
│   ├── core/                     # Core functionality
│   │   └── observability.py      # Metrics and tracing
│   ├── services/                 # Business logic
│   │   ├── groq_langchain_rag.py # RAG implementation
│   │   └── vectorstore.py        # Vector operations
│   └── main.py                   # FastAPI application
├── evals/                        # Evaluation scripts
│   ├── datasets/                 # Test datasets
│   └── run_eval.py              # Evaluation runner
├── monitoring/                   # Monitoring configuration
│   ├── grafana/                  # Grafana dashboards
│   └── prometheus-local.yml      # Prometheus config
├── ui_app.py                     # Streamlit interface
├── rag_mock_api.py              # Mock API for testing
└── requirements.txt              # Dependencies
```

## 🚧 Development Status

### ✅ Completed Features
- [x] Core RAG implementation with LangChain
- [x] LangSmith tracing integration
- [x] Prometheus metrics collection
- [x] Grafana dashboard configuration
- [x] Docker containerization
- [x] Basic evaluation framework
- [x] Streamlit UI interface

### 🚧 In Progress
- [ ] Real-time RAG API deployment
- [ ] Advanced evaluation metrics
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Load testing

### 📋 Planned Features
- [ ] Multi-tenant support
- [ ] Advanced caching strategies
- [ ] Custom model fine-tuning
- [ ] API rate limiting
- [ ] Advanced analytics
- [ ] Mobile app integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the RAG framework
- [LangSmith](https://smith.langchain.com/) for tracing and evaluation
- [Groq](https://groq.com/) for high-performance inference
- [Prometheus](https://prometheus.io/) for metrics collection
- [Grafana](https://grafana.com/) for visualization

## 📞 Support

For questions and support:
- Create an issue in this repository
- Check the [documentation](docs/)
- Review the [troubleshooting guide](docs/troubleshooting.md)

---

**Status**: 🚧 In Development | **Last Updated**: January 2025 | **Version**: 0.1.0