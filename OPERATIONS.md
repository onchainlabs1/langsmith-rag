# Operations Guide

## Deployment

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenAI API key
- LangSmith API key

### Environment Setup

1. **Clone and Install**
```bash
git clone <repository-url>
cd langsmith-demo
make install
```

2. **Configure Environment**
```bash
cp env.example .env
# Edit .env with your API keys
```

3. **Initialize Knowledge Base**
```bash
# Knowledge base will be created automatically on first run
# Place markdown files in data/knowledge/
```

### Production Deployment

#### Docker Deployment

```bash
# Build image
make docker-build

# Run container
make docker-run
```

#### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LANGCHAIN_API_KEY` | LangSmith API key | - | Yes |
| `LANGCHAIN_PROJECT` | LangSmith project name | langsmith-demo | No |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `ENVIRONMENT` | Deployment environment | development | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `VECTORSTORE_PATH` | Vectorstore directory | ./data/vectorstore | No |

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Response format
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Logging

The application uses structured JSON logging with the following fields:

- `timestamp`: ISO 8601 timestamp
- `level`: Log level (INFO, WARNING, ERROR)
- `logger`: Logger name
- `message`: Log message
- `request_id`: Unique request identifier
- `extra_fields`: Additional context

### Monitoring Endpoints

- `GET /health` - Service health status
- `GET /metrics` - Performance metrics (if implemented)
- `GET /docs` - API documentation

## Maintenance

### Knowledge Base Updates

1. **Add New Documents**
```bash
# Place markdown files in data/knowledge/
# Restart service to reload vectorstore
```

2. **Update Vectorstore**
```bash
# Delete existing vectorstore
rm -rf data/vectorstore/*

# Restart service to rebuild
```

### Evaluation Management

1. **Run Offline Evaluation**
```bash
make eval-offline
```

2. **Check Evaluation Results**
```bash
# Results saved to evals/reports/{timestamp}_run/
cat evals/reports/*/evaluation_report.json
```

3. **Quality Gate Status**
```bash
# Check if thresholds are met
python -c "
import json
with open('evals/reports/*/evaluation_report.json') as f:
    report = json.load(f)
    print(f'Groundedness: {report[\"avg_groundedness\"]:.3f}')
    print(f'Correctness: {report[\"avg_correctness\"]:.3f}')
    print(f'Passed: {report[\"passed_threshold\"]}')
"
```

### Backup and Recovery

1. **Backup Vectorstore**
```bash
tar -czf vectorstore_backup.tar.gz data/vectorstore/
```

2. **Backup Evaluation Reports**
```bash
tar -czf evaluation_reports_backup.tar.gz evals/reports/
```

3. **Restore from Backup**
```bash
tar -xzf vectorstore_backup.tar.gz
tar -xzf evaluation_reports_backup.tar.gz
```

## Troubleshooting

### Common Issues

#### 1. Vectorstore Not Found
```
FileNotFoundError: Vectorstore not found at ./data/vectorstore
```

**Solution:**
```bash
# Initialize knowledge base
python -c "
from src.services.vectorstore import VectorStoreService
service = VectorStoreService()
service.load_knowledge_base()
"
```

#### 2. API Key Issues
```
Error: OpenAI API key not found
```

**Solution:**
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $LANGCHAIN_API_KEY

# Update .env file
vim .env
```

#### 3. Evaluation Failures
```
Evaluation failed: Thresholds not met
```

**Solution:**
```bash
# Check evaluation results
cat evals/reports/*/evaluation_report.json

# Improve knowledge base or adjust thresholds
```

### Performance Issues

#### 1. Slow Response Times
- Check vectorstore size
- Optimize chunk size
- Monitor API rate limits
- Check network connectivity

#### 2. High Memory Usage
- Monitor vectorstore size
- Check for memory leaks
- Optimize chunking strategy
- Consider vectorstore sharding

#### 3. Evaluation Timeouts
- Reduce dataset size
- Optimize evaluation metrics
- Use parallel processing
- Check resource limits

### Debugging

#### 1. Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
uvicorn src.main:app --reload
```

#### 2. Check LangSmith Traces
```bash
# View traces in LangSmith dashboard
# Check trace URLs in API responses
```

#### 3. Test Individual Components
```bash
# Test vectorstore
python -c "
from src.services.vectorstore import VectorStoreService
service = VectorStoreService()
service.load_vectorstore()
print('Vectorstore loaded successfully')
"

# Test RAG service
python -c "
from src.services.vectorstore import VectorStoreService
from src.services.rag import RAGService
vectorstore = VectorStoreService()
vectorstore.load_vectorstore()
rag = RAGService(vectorstore)
result = rag.answer_question('What is ISO 42001?')
print(result)
"
```

## Security

### API Security
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Sanitize error messages

### Data Protection
- Secure API key storage
- Encrypt sensitive data
- Implement access controls
- Regular security audits

### Compliance
- Maintain audit trails
- Document security measures
- Regular vulnerability assessments
- Compliance monitoring

## Scaling

### Horizontal Scaling
- Use load balancers
- Implement session affinity
- Share vectorstore across instances
- Monitor resource usage

### Vertical Scaling
- Optimize memory usage
- Tune JVM parameters
- Monitor CPU utilization
- Implement caching strategies

### Data Scaling
- Optimize vectorstore size
- Implement sharding
- Use distributed storage
- Monitor performance metrics

## Disaster Recovery

### Backup Strategy
- Regular vectorstore backups
- Evaluation report archives
- Configuration backups
- Code repository backups

### Recovery Procedures
- Restore from backups
- Rebuild vectorstore
- Restart services
- Verify functionality

### Business Continuity
- Monitor service health
- Implement failover
- Maintain documentation
- Regular testing
