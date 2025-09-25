# EU AI Act Compliance RAG System - Deployment Guide

## 🚀 Production Deployment

This guide covers deploying the EU AI Act Compliance RAG System in production using Docker Compose.

## 📋 Prerequisites

### System Requirements
- **Docker**: Version 20.10+ 
- **Docker Compose**: Version 2.0+
- **Memory**: Minimum 4GB RAM
- **Storage**: 10GB free space
- **Network**: Internet access for API calls

### API Keys Required
- **OpenAI API Key**: For LLM inference
- **LangSmith API Key**: For tracing and evaluation

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI API   │    │ Vectorstore Init│
│   Port: 8501    │    │   Port: 8000    │    │   (One-time)    │
│                 │    │                 │    │                 │
│  - Query Input  │    │  - RAG Pipeline │    │  - AI Act Index │
│  - Results UI   │    │  - LangSmith     │    │  - FAISS Build  │
│  - Health Check │    │  - Health Check  │    │  - Corpus Load  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Shared Network │
                    │  ai-act-network │
                    └─────────────────┘
```

## 🔧 Quick Deployment

### 1. Clone and Setup
```bash
git clone <repository-url>
cd langsmith-demo
cp env.example .env
```

### 2. Configure Environment
Edit `.env` file with your API keys:
```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here

# Optional Configuration
LANGCHAIN_PROJECT=langsmith-demo
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=your_secure_secret_key_here
```

### 3. Deploy Services
```bash
# Start all services
make compose-up

# Check status
make compose-status

# View logs
make logs
```

### 4. Verify Deployment
```bash
# Check API health
curl http://localhost:8000/health

# Check UI
curl http://localhost:8501/_stcore/health

# Test compliance query
curl -X POST http://localhost:8000/v1/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the prohibited AI practices?"}'
```

## 📊 Service Details

### API Service (FastAPI)
- **Port**: 8000
- **Health Check**: `/health`
- **API Docs**: `/docs`
- **Main Endpoint**: `/v1/answer`
- **Features**:
  - EU AI Act compliance RAG pipeline
  - LangSmith tracing integration
  - FAISS vectorstore with AI Act corpus
  - Comprehensive error handling

### UI Service (Streamlit)
- **Port**: 8501
- **Health Check**: `/_stcore/health`
- **Features**:
  - Interactive compliance query interface
  - Real-time API health monitoring
  - Rich results display with sources
  - Query history and session management

### Vectorstore Init Service
- **Purpose**: One-time AI Act corpus indexing
- **Process**:
  - Loads EU AI Act documents from `data/knowledge/ai_act/`
  - Creates FAISS vectorstore with compliance-focused chunking
  - Extracts risk categories and article references
  - Saves vectorstore to shared volume

## 🔍 Monitoring and Logs

### View Logs
```bash
# All services
make logs

# Specific service
docker-compose logs -f api
docker-compose logs -f ui

# Last 100 lines
docker-compose logs --tail=100
```

### Health Checks
```bash
# Check service status
make compose-status

# Manual health checks
curl http://localhost:8000/health
curl http://localhost:8501/_stcore/health
```

### Service Management
```bash
# Restart services
make compose-restart

# Stop services
make compose-down

# Clean up resources
make compose-clean
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM | - | Yes |
| `LANGCHAIN_API_KEY` | LangSmith API key | - | Yes |
| `LANGCHAIN_PROJECT` | LangSmith project name | langsmith-demo | No |
| `ENVIRONMENT` | Deployment environment | production | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `SECRET_KEY` | Application secret key | - | Yes |

### Docker Compose Configuration

The `docker-compose.yml` includes:
- **Service Dependencies**: UI depends on API, API depends on vectorstore init
- **Health Checks**: Automated health monitoring for all services
- **Volume Mounts**: Persistent data storage for vectorstore and reports
- **Network**: Internal communication between services
- **Restart Policies**: Automatic restart on failure

### Resource Limits

For production deployment, consider adding resource limits:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

## 🔒 Security Considerations

### API Key Management
- Store API keys in `.env` file (not in version control)
- Use Docker secrets for production deployments
- Rotate API keys regularly
- Monitor API usage and costs

### Network Security
- Services communicate over internal Docker network
- No external database dependencies
- Health checks use internal endpoints
- Consider reverse proxy for production

### Data Protection
- Vectorstore data is stored in Docker volumes
- No persistent user data storage
- Logs may contain query information (review retention policies)
- Consider PII redaction for production logs

## 📈 Scaling Considerations

### Horizontal Scaling
- API service can be scaled with multiple replicas
- Load balancer required for multiple API instances
- Shared vectorstore volume for consistency
- Consider external vectorstore for large deployments

### Vertical Scaling
- Increase memory for larger vectorstores
- Add CPU for faster inference
- Monitor resource usage with Docker stats
- Consider GPU acceleration for large models

### Performance Optimization
- Enable response caching for common queries
- Optimize vectorstore size and chunking
- Monitor API response times
- Consider CDN for static assets

## 🚨 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker Compose configuration
docker-compose config

# Check logs for errors
make logs

# Verify environment variables
docker-compose exec api env | grep API_KEY
```

#### API Health Check Fails
```bash
# Check if API is running
docker-compose ps

# Check API logs
docker-compose logs api

# Test API directly
docker-compose exec api curl localhost:8000/health
```

#### UI Not Loading
```bash
# Check UI service status
docker-compose ps ui

# Check UI logs
docker-compose logs ui

# Verify network connectivity
docker-compose exec ui curl http://api:8000/health
```

#### Vectorstore Issues
```bash
# Check vectorstore init logs
docker-compose logs vectorstore-init

# Verify corpus files exist
docker-compose exec api ls -la data/knowledge/ai_act/

# Rebuild vectorstore
docker-compose down
docker-compose up vectorstore-init
```

### Performance Issues

#### Slow Response Times
- Check API logs for errors
- Monitor resource usage: `docker stats`
- Verify API key limits and quotas
- Check network connectivity

#### High Memory Usage
- Monitor vectorstore size
- Check for memory leaks in logs
- Consider reducing chunk size
- Optimize Docker resource limits

## 🔄 Updates and Maintenance

### Updating the System
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
make compose-down
make compose-build
make compose-up
```

### Backup and Recovery
```bash
# Backup vectorstore
docker-compose exec api tar -czf /tmp/vectorstore-backup.tar.gz data/vectorstore/

# Backup evaluation reports
docker-compose exec api tar -czf /tmp/reports-backup.tar.gz evals/reports/

# Restore from backup
docker-compose exec api tar -xzf /tmp/vectorstore-backup.tar.gz -C /
```

### Monitoring and Alerts
- Set up health check monitoring
- Monitor API response times
- Track error rates and patterns
- Set up alerts for service failures

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)

### Support
- Check logs for detailed error information
- Review API documentation at `/docs` endpoint
- Monitor service health and performance
- Consider professional support for production deployments

This deployment guide provides comprehensive instructions for deploying the EU AI Act Compliance RAG System in production environments with Docker Compose.
