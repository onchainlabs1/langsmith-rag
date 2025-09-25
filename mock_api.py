#!/usr/bin/env python3
"""Mock API server for EU AI Act Compliance RAG System."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class MockAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "healthy", "service": "EU AI Act Compliance RAG API"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/v1/answer':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Mock response
            answer = f"""
            Based on the EU AI Act, a system is considered high-risk if it meets specific criteria outlined in Article 6. 
            
            The main categories of high-risk AI systems include:
            
            1. **Biometric identification and categorization** of natural persons
            2. **Management and operation** of critical infrastructure  
            3. **Education and vocational training** systems
            4. **Employment, worker management** and access to self-employment
            5. **Access to and enjoyment of essential private services** and public services and benefits
            6. **Law enforcement** systems
            7. **Migration, asylum and border control** management
            8. **Administration of justice** and democratic processes
            
            These systems are subject to strict compliance requirements including risk management, data governance, 
            technical documentation, record keeping, transparency and provision of information to users, 
            human oversight, and accuracy, robustness and cybersecurity.
            
            The EU AI Act aims to ensure that AI systems are safe, transparent, traceable, non-discriminatory 
            and environmentally friendly, while respecting fundamental rights.
            """
            
            sources = [
                {
                    "filename": "EU AI Act Article 6",
                    "content": "High-risk AI systems are those that pose a high risk to the health, safety or fundamental rights of natural persons.",
                    "source": "Official Journal of the European Union",
                    "similarity_score": 0.95
                },
                {
                    "filename": "EU AI Act Annex I", 
                    "content": "List of high-risk AI systems including biometric identification, critical infrastructure, education, employment, and law enforcement systems.",
                    "source": "Official Journal of the European Union",
                    "similarity_score": 0.92
                }
            ]
            
            response = {
                "answer": answer.strip(),
                "sources": sources,
                "trace_url": "https://smith.langchain.com/traces/mock-trace-id"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), MockAPIHandler)
    print("🚀 Mock API server running on http://localhost:8000")
    print("📋 Available endpoints:")
    print("   GET  /health - Health check")
    print("   POST /v1/answer - Answer questions")
    print("🛑 Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()
