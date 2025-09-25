# EU AI Act Compliance RAG System - Observability Guide

## 🔍 Overview

This guide covers the complete observability stack for the EU AI Act Compliance RAG System, including monitoring, alerting, and performance analysis.

## 📊 Monitoring Stack

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Observability Stack                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Prometheus  │    │   Grafana   │    │    Loki     │     │
│  │ Port: 9090  │    │ Port: 3000  │    │ Port: 3100 │     │
│  │             │    │             │    │             │     │
│  │ - Metrics   │    │ - Dashboards│    │ - Logs      │     │
│  │ - Alerts    │    │ - SLOs      │    │ - Search    │     │
│  │ - SLOs      │    │ - Analysis  │    │ - Analysis  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │           │
│         └───────────────────┼───────────────────┘           │
│                             │                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              EU AI Act RAG API                         │ │
│  │              - OpenTelemetry Traces                    │ │
│  │              - Prometheus Metrics                     │ │
│  │              - Structured Logs                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Start Observability Stack
```bash
# Start monitoring services
make observe-up

# Start full stack with observability
make observe-full

# Check status
make observe-status

# View logs
make observe-logs
```

### Access Monitoring Tools
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100

## 📈 Metrics and SLOs

### Service Level Objectives (SLOs)
- **Latency**: 95th percentile ≤ 2.5s
- **Error Rate**: ≤ 1% (5xx errors)
- **Groundedness**: Average ≥ 0.75
- **Availability**: ≥ 99.9%

### Key Metrics

#### Request Metrics
- `rag_requests_total`: Total RAG requests
- `rag_request_duration_seconds`: Request duration histogram
- `rag_active_requests`: Currently active requests
- `rag_errors_total`: Total errors by type

#### RAG Pipeline Metrics
- `rag_retrieval_duration_seconds`: Document retrieval time
- `rag_llm_duration_seconds`: LLM inference time
- `rag_retrieval_k`: Number of documents retrieved
- `rag_groundedness_score`: Groundedness scores
- `rag_correctness_score`: Correctness scores

#### System Metrics
- `process_resident_memory_bytes`: Memory usage
- `process_cpu_seconds_total`: CPU usage
- `up`: Service availability

## 🎯 Grafana Dashboards

### EU AI Act Compliance Dashboard
**URL**: http://localhost:3000/d/eu-ai-act-dashboard

#### Panels
1. **Request Rate**: Requests per second
2. **Error Rate**: Error percentage
3. **Response Time**: 95th percentile latency
4. **Groundedness Score**: Average groundedness
5. **Request Duration Over Time**: Latency trends
6. **RAG Pipeline Components**: Retrieval vs LLM time
7. **Active Requests**: Current load
8. **Retrieval K Distribution**: Document count trends

### Custom Queries

#### Latency Analysis
```promql
# 95th percentile latency
histogram_quantile(0.95, rate(rag_request_duration_seconds_bucket[5m]))

# Average latency
rate(rag_request_duration_seconds_sum[5m]) / rate(rag_request_duration_seconds_count[5m])
```

#### Error Rate Analysis
```promql
# Error rate percentage
rate(rag_errors_total[5m]) / rate(rag_requests_total[5m]) * 100

# Error rate by endpoint
rate(rag_errors_total[5m]) by (endpoint)
```

#### Groundedness Analysis
```promql
# Average groundedness
histogram_quantile(0.50, rate(rag_groundedness_score_bucket[10m]))

# Groundedness distribution
histogram_quantile(0.95, rate(rag_groundedness_score_bucket[10m]))
```

## 🚨 Alerting Rules

### Critical Alerts
- **Service Down**: API service not responding
- **High Error Rate**: Error rate > 1%
- **High Memory Usage**: Memory > 2GB

### Warning Alerts
- **High Latency**: 95th percentile > 2.5s
- **Low Groundedness**: Average < 0.75
- **Rate Limit Exceeded**: Frequent 429 responses

### Alert Configuration
```yaml
# Example alert rule
- alert: HighLatency
  expr: histogram_quantile(0.95, rate(rag_request_duration_seconds_bucket[5m])) > 2.5
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High latency detected"
    description: "95th percentile latency is {{ $value }}s"
```

## 📊 Performance Testing

### k6 Load Testing
```bash
# Run performance tests
k6 run tests/performance/k6-load-test.js

# With custom parameters
k6 run --env API_BASE_URL=http://localhost:8000 tests/performance/k6-load-test.js
```

### Test Scenarios
1. **Ramp-up Test**: 0 → 10 → 20 users over 9 minutes
2. **Sustained Load**: 20 users for 5 minutes
3. **SLO Validation**: p95 < 2.5s, error rate < 1%

### Performance Thresholds
- **Response Time**: p95 < 2.5s
- **Error Rate**: < 1%
- **Throughput**: > 10 req/s
- **Availability**: > 99.9%

## 🔧 Configuration

### Environment Variables
```bash
# Observability Configuration
OTLP_ENDPOINT=http://tempo:4317
PROMETHEUS_PORT=8001
LOG_LEVEL=INFO

# JWT Configuration
JWT_SECRET=your-jwt-secret
JWT_ISSUER=eu-ai-act-api
JWT_AUDIENCE=eu-ai-act-users

# Monitoring
GRAFANA_PASSWORD=admin
```

### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'eu-ai-act-api'
    static_configs:
      - targets: ['api:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Configuration
```yaml
# monitoring/grafana/provisioning/datasources/prometheus.yml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
```

## 📝 Logging

### Structured Logging
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "src.api.routes",
  "message": "Processing EU AI Act compliance question",
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "analyst",
  "duration": 1.234,
  "compliance_focus": true
}
```

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information about operations
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors requiring immediate attention

### Log Analysis with Loki
```logql
# Error logs
{job="eu-ai-act-api"} |= "ERROR"

# High latency requests
{job="eu-ai-act-api"} | json | duration > 2.5

# User activity
{job="eu-ai-act-api"} | json | user_id="analyst"
```

## 🔍 Troubleshooting

### Common Issues

#### High Latency
1. Check retrieval performance
2. Monitor LLM response times
3. Verify vectorstore performance
4. Check system resources

#### High Error Rate
1. Review error logs
2. Check authentication issues
3. Verify rate limiting
4. Monitor system health

#### Low Groundedness
1. Check document retrieval quality
2. Verify chunking strategy
3. Monitor LLM responses
4. Review evaluation results

### Debugging Commands
```bash
# Check service status
make observe-status

# View logs
make observe-logs

# Check metrics
curl http://localhost:8001/metrics

# Test endpoints
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/v1/answer \
  -d '{"question": "What are prohibited AI practices?"}'
```

## 📚 Best Practices

### Monitoring
1. **Set up alerts** for critical SLOs
2. **Monitor trends** over time
3. **Track user behavior** and patterns
4. **Regular review** of dashboards

### Performance
1. **Baseline performance** before changes
2. **Load test** regularly
3. **Monitor resource usage**
4. **Optimize bottlenecks**

### Security
1. **Monitor authentication** failures
2. **Track rate limiting** effectiveness
3. **Audit user access** patterns
4. **Review security logs**

## 🔮 Advanced Features

### Custom Metrics
```python
# Add custom metrics
from src.core.observability import get_observability_service

observability = get_observability_service()
observability.record_groundedness(score, request_id)
```

### Custom Dashboards
1. Create dashboard JSON
2. Place in `monitoring/grafana/dashboards/`
3. Restart Grafana service
4. Access via Grafana UI

### Alert Channels
1. **Email**: Configure SMTP settings
2. **Slack**: Webhook integration
3. **PagerDuty**: Incident management
4. **Webhook**: Custom integrations

This observability guide provides comprehensive monitoring and alerting capabilities for the EU AI Act Compliance RAG System, ensuring production-ready observability and performance monitoring.
