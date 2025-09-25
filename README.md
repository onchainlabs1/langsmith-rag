# 🚀 LangSmith RAG - EU AI Act Compliance System

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)](https://python.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-0.23+-purple.svg)](https://groq.com/)
[![LangSmith](https://img.shields.io/badge/LangSmith-0.3+-red.svg)](https://smith.langchain.com/)

> **RAG system specialized in EU AI Act compliance using LangChain, Groq and LangSmith for ultra-fast inference and complete monitoring.**

## 🌟 Key Features

- ⚡ **Ultra-Fast Inference**: Groq with ~300 tokens/second (6x faster than OpenAI)
- 💰 **Cost-Effective**: ~10x cheaper than OpenAI
- 🔍 **Complete Monitoring**: Automatic traces in LangSmith
- ⚖️ **Compliance Focus**: Specialized in EU AI Act
- 🛡️ **Security**: JWT authentication and complete observability
- 🌍 **EU-Friendly**: No data residency restrictions
- 📊 **Observability**: Prometheus metrics and Grafana
- 🔄 **Auto-Detection**: Groq > OpenAI > Mock automatically

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI API   │    │   LangSmith     │
│                 │◄──►│                 │◄──►│   Tracing       │
│  User Interface │    │  REST Endpoints │    │   Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Groq LLM      │    │   LangChain     │    │   Vector Store  │
│                 │◄──►│   RAG Pipeline  │◄──►│   FAISS         │
│  Ultra-Fast     │    │   Orchestration │    │   Embeddings    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. **Clone the Repository**

```bash
git clone https://github.com/onchainlabs1/langsmith-rag.git
cd langsmith-rag
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 3. **Configure API Keys**

```bash
# Groq API Key (FREE)
export GROQ_API_KEY="gsk_your_groq_key_here"

# LangSmith API Key (FREE - 5,000 traces/month)
export LANGCHAIN_API_KEY="ls__your_langsmith_key_here"

# OpenAI API Key (for embeddings)
export OPENAI_API_KEY="sk-your_openai_key_here"

# LangSmith Configuration
export LANGCHAIN_PROJECT="groq-eu-ai-act-compliance"
export LANGCHAIN_TRACING_V2=true
```

### 4. **Test Configuration**

```bash
# Test LangSmith
python3 test_langsmith_config.py

# Test complete system
python3 test_groq_langchain.py
```

### 5. **Start Server**

```bash
uvicorn src.main:app --reload
```

### 6. **Access Interface**

- **API Documentation**: http://localhost:8000/docs
- **Streamlit UI**: `streamlit run ui_app.py`
- **LangSmith Traces**: https://smith.langchain.com/

## 📋 How to Get API Keys

### **Groq API Key (FREE)**
1. Visit [console.groq.com/keys](https://console.groq.com/keys)
2. Login/create account
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

### **LangSmith API Key (FREE)**
1. Visit [smith.langchain.com](https://smith.langchain.com/)
2. Login with GitHub
3. Settings > API Keys > Create API Key
4. Copy the key (starts with `ls__...`)

### **OpenAI API Key**
1. Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create new key
3. Copy the key (starts with `sk-...`)

## 🧪 Testing

```bash
# Test LangSmith configuration
python3 test_langsmith_config.py

# Test Groq system
python3 test_groq_langchain.py

# Test API endpoints
python3 test_api_langchain.py

# Test mock (without API keys)
python3 test_mock_langchain.py
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/langchain/health` | Health check |
| `POST` | `/v1/langchain/setup` | Initialize RAG system |
| `POST` | `/v1/langchain/ask` | Ask questions about EU AI Act |
| `GET` | `/v1/langchain/similar/{query}` | Search similar documents |
| `GET` | `/v1/langchain/info` | System information |
| `POST` | `/v1/auth/login` | JWT authentication |

### **Usage Example**

```bash
# Login
curl -X POST "http://localhost:8000/v1/auth/login" \
     -d "username=analyst&password=analyst"

# Setup
curl -X POST "http://localhost:8000/v1/langchain/setup" \
     -H "Authorization: Bearer $JWT_TOKEN"

# Ask question
curl -X POST "http://localhost:8000/v1/langchain/ask" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $JWT_TOKEN" \
     -d '{"question": "What are high-risk AI systems under the EU AI Act?"}'
```

## 📊 Performance

### **LLM Comparison**

| Metric | Groq | OpenAI | Mock |
|---------|------|--------|------|
| Speed | 300 tok/s | 50 tok/s | Instant |
| Cost | $0.10/1M | $1.00/1M | Free |
| Quality | Excellent | Excellent | Basic |
| LangSmith | ✅ | ✅ | ❌ |

### **Groq Benefits**

- ⚡ **6x faster** than OpenAI
- 💰 **10x cheaper** than OpenAI
- 🔓 **Open-source models** (Llama, Mixtral)
- 🌍 **No data restrictions** (stays in EU)
- ⚖️ **GDPR-friendly**

## 🛠️ Development

### **Project Structure**

```
langsmith-rag/
├── src/
│   ├── api/                    # API endpoints
│   ├── app/services/           # Advanced services
│   ├── core/                   # Configuration and security
│   ├── services/               # LangChain services
│   └── main.py                 # FastAPI application
├── tests/                      # Automated tests
├── monitoring/                 # Prometheus/Grafana configuration
├── docs/                       # Documentation
└── requirements.txt            # Dependencies
```

### **Development Scripts**

```bash
# Development
uvicorn src.main:app --reload

# Testing
pytest tests/

# Linting
ruff src/
mypy src/

# Docker
make docker-build
make docker-run
```

## 🐳 Docker

```bash
# Build
docker build -t langsmith-rag .

# Run
docker run -p 8000:8000 \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  langsmith-rag
```

## 📈 Monitoring

### **Prometheus Metrics**
- Access: http://localhost:8000/metrics

### **Grafana Dashboard**
- Configuration in `monitoring/grafana/`

### **LangSmith Traces**
- Access: https://smith.langchain.com/
- Project: `groq-eu-ai-act-compliance`

## 🔒 Security

- ✅ JWT authentication
- ✅ Rate limiting
- ✅ Input validation
- ✅ Error handling
- ✅ Complete observability
- ✅ Structured logs

## 📚 Documentation

- [LangChain Implementation Guide](LANGCHAIN_IMPLEMENTATION_GUIDE.md)
- [Groq + LangSmith Setup](GROQ_LANGSMITH_SETUP.md)
- [System Architecture](ARCHITECTURE.md)
- [Observability](OBSERVABILITY.md)
- [Security](SECURITY.md)

## 🤝 Contributing

1. Fork the project
2. Create a branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://python.langchain.com/) - LLM Framework
- [Groq](https://groq.com/) - Ultra-fast inference
- [LangSmith](https://smith.langchain.com/) - Monitoring and tracing
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Streamlit](https://streamlit.io/) - User interface

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/onchainlabs1/langsmith-rag/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/onchainlabs1/langsmith-rag/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/onchainlabs1/langsmith-rag/discussions)

---

**Developed with ❤️ for EU AI Act compliance**

⭐ **If this project was useful, consider giving it a star!**
