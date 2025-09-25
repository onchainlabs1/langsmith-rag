import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2500'], // 95th percentile < 2.5s
    error_rate: ['rate<0.01'],         // Error rate < 1%
    http_req_failed: ['rate<0.01'],   // Failed requests < 1%
  },
};

// Test data
const API_BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8000';
const JWT_TOKEN = __ENV.JWT_TOKEN || '';

// Test questions
const questions = [
  'What are the prohibited AI practices under the EU AI Act?',
  'What qualifies a system as high-risk under the EU AI Act?',
  'What are the requirements for high-risk AI systems?',
  'What are the transparency obligations for AI systems?',
  'What are the penalties for non-compliance with the EU AI Act?'
];

export function setup() {
  // Login to get JWT token if not provided
  if (!JWT_TOKEN) {
    const loginResponse = http.post(`${API_BASE_URL}/v1/auth/login`, JSON.stringify({
      username: 'analyst',
      password: 'password'
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (loginResponse.status === 200) {
      const loginData = JSON.parse(loginResponse.body);
      return loginData.access_token;
    }
  }
  
  return JWT_TOKEN;
}

export default function(token) {
  // Select random question
  const question = questions[Math.floor(Math.random() * questions.length)];
  
  // Make request to /v1/answer endpoint
  const response = http.post(`${API_BASE_URL}/v1/answer`, JSON.stringify({
    question: question
  }), {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
  });
  
  // Check response
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response has answer': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.answer && data.answer.length > 0;
      } catch (e) {
        return false;
      }
    },
    'response has sources': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.sources && Array.isArray(data.sources);
      } catch (e) {
        return false;
      }
    },
    'response time < 5s': (r) => r.timings.duration < 5000,
  });
  
  // Record metrics
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
  
  // Sleep between requests
  sleep(1);
}

export function teardown(data) {
  console.log('Load test completed');
}
