#!/usr/bin/env python3
"""
RAG Mock API - Generates realistic RAG metrics for Grafana
Simulates a real RAG system with proper metrics
"""

import time
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from prometheus_client import start_http_server, Counter, Histogram, Gauge, generate_latest
import os

# Prometheus Metrics
rag_requests_total = Counter('rag_requests_total', 'Total RAG requests', ['status'])
rag_request_duration = Histogram('rag_request_duration_seconds', 'RAG request duration', ['stage'])
rag_tokens_total = Counter('rag_tokens_total', 'Total tokens processed', ['type'])
rag_cost_usd = Counter('rag_cost_usd_total', 'Total cost in USD')
rag_citations_count = Histogram('rag_citations_per_response', 'Citations per response')
rag_accuracy_score = Gauge('rag_accuracy_score', 'RAG accuracy score (0-1)')
rag_response_time = Gauge('rag_response_time_seconds', 'Current response time')

# Simulated RAG metrics
class RAGMetricsSimulator:
    def __init__(self):
        self.base_requests_per_minute = 15
        self.base_response_time = 1.2
        self.base_accuracy = 0.85
        self.base_citations = 3.5
        
    def simulate_request(self):
        """Simulate a single RAG request"""
        # Request metrics
        status = random.choices(['success', 'error'], weights=[0.95, 0.05])[0]
        rag_requests_total.labels(status=status).inc()
        
        if status == 'success':
            # Simulate processing stages
            stages = ['retrieval', 'generation', 'postprocess']
            total_duration = 0
            
            for stage in stages:
                duration = random.uniform(0.3, 0.8)
                rag_request_duration.labels(stage=stage).observe(duration)
                total_duration += duration
            
            # Token metrics
            input_tokens = random.randint(50, 200)
            output_tokens = random.randint(30, 150)
            rag_tokens_total.labels(type='input').inc(input_tokens)
            rag_tokens_total.labels(type='output').inc(output_tokens)
            
            # Cost calculation (approximate)
            cost = (input_tokens * 0.0000015 + output_tokens * 0.000002) * 1.1
            rag_cost_usd.inc(cost)
            
            # Citations and accuracy
            citations = random.randint(1, 8)
            rag_citations_count.observe(citations)
            
            accuracy = random.uniform(0.75, 0.95)
            rag_accuracy_score.set(accuracy)
            
            # Update response time
            rag_response_time.set(total_duration)
            
            return {
                'status': status,
                'duration': total_duration,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost': cost,
                'citations': citations,
                'accuracy': accuracy
            }
        else:
            # Error case
            rag_accuracy_score.set(0.0)
            return {'status': status, 'error': 'Simulated error'}

class RAGMockAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, simulator, *args, **kwargs):
        self.simulator = simulator
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            # Prometheus metrics endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(generate_latest().encode())
            
        elif self.path == '/health':
            # Health check
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy', 'timestamp': time.time()}
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/simulate':
            # Simulate a RAG request
            result = self.simulator.simulate_request()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        else:
            self.send_response(404)
            self.end_headers()

def create_handler(simulator):
    def handler(*args, **kwargs):
        return RAGMockAPIHandler(simulator, *args, **kwargs)
    return handler

def run_simulation_loop(simulator):
    """Run continuous simulation of RAG requests"""
    while True:
        # Simulate variable request rate
        requests_this_cycle = random.randint(3, 8)
        
        for _ in range(requests_this_cycle):
            simulator.simulate_request()
            time.sleep(random.uniform(0.1, 0.3))
        
        # Wait before next cycle
        time.sleep(random.uniform(10, 30))

def main():
    print("🚀 Starting RAG Mock API with Real Metrics...")
    
    # Create simulator
    simulator = RAGMetricsSimulator()
    
    # Start Prometheus metrics server
    port = 8001
    print(f"📊 Starting Prometheus metrics on port {port}")
    start_http_server(port)
    
    # Start simulation loop in background
    simulation_thread = threading.Thread(target=run_simulation_loop, args=(simulator,))
    simulation_thread.daemon = True
    simulation_thread.start()
    
    # Start HTTP server for additional endpoints
    handler = create_handler(simulator)
    http_server = HTTPServer(('localhost', 8002), handler)
    
    print(f"🌐 RAG Mock API running on:")
    print(f"   Metrics: http://localhost:{port}/metrics")
    print(f"   Health:  http://localhost:8002/health")
    print(f"   Simulate: http://localhost:8002/simulate")
    print(f"📈 Generating realistic RAG metrics...")
    print(f"🎯 Check Grafana: http://localhost:3000")
    
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down RAG Mock API...")
        http_server.shutdown()

if __name__ == "__main__":
    main()
