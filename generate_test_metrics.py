#!/usr/bin/env python3
"""Generate test metrics for Grafana dashboard."""

import time
import random
import requests
import json
from datetime import datetime

def generate_test_metrics():
    """Generate test metrics that simulate RAG system data."""
    
    # Simulate metrics data
    metrics = {
        "rag_requests_total": random.randint(100, 500),
        "rag_request_duration_seconds": round(random.uniform(0.5, 3.0), 2),
        "rag_errors_total": random.randint(0, 10),
        "rag_input_tokens_total": random.randint(1000, 5000),
        "rag_output_tokens_total": random.randint(500, 2000),
        "rag_cost_usd_total": round(random.uniform(0.01, 0.50), 4),
        "rag_citation_validity_score": round(random.uniform(0.7, 1.0), 2),
        "rag_citations_per_response": random.randint(2, 8)
    }
    
    return metrics

def send_metrics_to_prometheus(metrics):
    """Send metrics to Prometheus (simulated)."""
    print(f"📊 Generated metrics at {datetime.now().strftime('%H:%M:%S')}:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    return True

def main():
    """Main function to generate test metrics."""
    print("🧪 GENERATING TEST METRICS FOR GRAFANA")
    print("======================================")
    print("")
    
    # Generate initial metrics
    print("1. Generating initial metrics...")
    metrics = generate_test_metrics()
    send_metrics_to_prometheus(metrics)
    
    print("")
    print("2. Simulating continuous data generation...")
    print("   (This simulates what would happen when RAG system is running)")
    
    # Simulate continuous data generation
    for i in range(5):
        time.sleep(2)
        print(f"   📈 Update {i+1}/5...")
        
        # Update metrics with some variation
        metrics = generate_test_metrics()
        send_metrics_to_prometheus(metrics)
    
    print("")
    print("✅ Test metrics generation complete!")
    print("")
    print("🎯 NEXT STEPS:")
    print("==============")
    print("1. Open Grafana: http://localhost:3000 (admin/admin)")
    print("2. Add Prometheus as data source: http://prometheus:9090")
    print("3. Create dashboard with these queries:")
    print("   - up * 10  # Simulated request rate")
    print("   - up * 2.5 # Simulated response time")
    print("   - up * 0.1 # Simulated error rate")
    print("4. Use 'up' metric as base for all visualizations")
    print("")
    print("💡 TIP: The 'up' metric shows if services are running")
    print("   Multiply by different factors to simulate RAG metrics")

if __name__ == "__main__":
    main()
