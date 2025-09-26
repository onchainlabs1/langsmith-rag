#!/bin/bash

echo "🧪 TESTING RAG SYSTEM METRICS"
echo "=============================="
echo ""

# Check if RAG API is running
echo "1. Checking if RAG API is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ RAG API is running on port 8000"
else
    echo "❌ RAG API is not running. Please start it with:"
    echo "   source setup_tracing.sh"
    echo "   uvicorn src.main:app --reload --port 8000"
    echo ""
    exit 1
fi

echo ""

# Check if metrics endpoint is working
echo "2. Checking metrics endpoint..."
if curl -s http://localhost:8000/metrics | grep -q "rag_requests_total"; then
    echo "✅ Metrics endpoint is working and showing RAG metrics"
else
    echo "❌ Metrics endpoint not working or no RAG metrics found"
    echo "   Metrics URL: http://localhost:8000/metrics"
    echo ""
fi

echo ""

# Check if Prometheus is scraping
echo "3. Checking Prometheus..."
if curl -s http://localhost:9090/api/v1/targets | grep -q "rag-api"; then
    echo "✅ Prometheus is configured to scrape RAG API"
else
    echo "⚠️  Prometheus may not be scraping RAG API yet"
    echo "   Prometheus URL: http://localhost:9090"
    echo ""
fi

echo ""

# Make a test query to generate metrics
echo "4. Making test query to generate metrics..."
RESPONSE=$(curl -s -X POST http://localhost:8000/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "What is the EU AI Act?"}')

if echo "$RESPONSE" | grep -q "answer"; then
    echo "✅ Test query successful - metrics should be generated"
else
    echo "❌ Test query failed"
    echo "   Response: $RESPONSE"
    echo ""
fi

echo ""

# Check metrics again
echo "5. Checking metrics after query..."
METRICS_COUNT=$(curl -s http://localhost:8000/metrics | grep -c "rag_")
echo "   Found $METRICS_COUNT RAG-related metrics"

echo ""

echo "📊 ACCESS URLs:"
echo "==============="
echo "Grafana:     http://localhost:3000 (admin/admin)"
echo "Prometheus:  http://localhost:9090"
echo "RAG API:     http://localhost:8000"
echo "Metrics:     http://localhost:8000/metrics"
echo ""

echo "🎯 NEXT STEPS:"
echo "=============="
echo "1. Open Grafana: open http://localhost:3000"
echo "2. Add Prometheus data source if not already done"
echo "3. Create dashboard with RAG metrics"
echo "4. Make more queries to see metrics update in real-time"
echo ""
