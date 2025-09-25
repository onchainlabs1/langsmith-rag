# EU AI Act Compliance RAG System - Security Guide

## 🔒 Security Overview

This guide covers the security implementation for the EU AI Act Compliance RAG System, including authentication, authorization, rate limiting, and security best practices.

## 🛡️ Security Architecture

### Authentication & Authorization
```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layer                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   JWT Auth  │    │    RBAC     │    │ Rate Limit  │     │
│  │             │    │             │    │             │     │
│  │ - Tokens    │    │ - Roles     │    │ - Per User  │     │
│  │ - Validation│    │ - Permissions│   │ - Per Role │     │
│  │ - Expiry    │    │ - Access    │    │ - Headers  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │           │
│         └───────────────────┼───────────────────┘           │
│                             │                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              EU AI Act RAG API                         │ │
│  │              - Protected Endpoints                     │ │
│  │              - User Context                           │ │
│  │              - Audit Logging                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Authentication

### JWT Token Flow
1. **Login Request**: User provides credentials
2. **Token Generation**: Server creates JWT with user claims
3. **Token Validation**: Each request validates JWT signature
4. **Token Expiry**: Tokens expire after configured time

### JWT Configuration
```bash
# Environment Variables
JWT_SECRET=your-secure-secret-key
JWT_ISSUER=eu-ai-act-api
JWT_AUDIENCE=eu-ai-act-users
JWT_EXPIRE_MINUTES=30
```

### Token Structure
```json
{
  "sub": "user_id",
  "username": "analyst",
  "role": "analyst",
  "iat": 1640995200,
  "exp": 1640997000,
  "iss": "eu-ai-act-api",
  "aud": "eu-ai-act-users"
}
```

## 👥 Role-Based Access Control (RBAC)

### User Roles
| Role | Permissions | Description |
|------|-------------|-------------|
| **admin** | read, write, evaluate, admin | Full system access |
| **analyst** | read, write, evaluate | Can run evaluations |
| **viewer** | read | Read-only access |

### Permission Matrix
| Endpoint | admin | analyst | viewer |
|----------|-------|---------|--------|
| `/health` | ✅ | ✅ | ✅ |
| `/v1/answer` | ✅ | ✅ | ✅ |
| `/v1/evaluate/offline` | ✅ | ✅ | ❌ |
| `/metrics` | ✅ | ✅ | ✅ |

### Role Implementation
```python
# Require specific permission
@router.post("/v1/evaluate/offline")
async def run_evaluation(
    current_user: User = Depends(require_evaluate)
):
    # Only analyst and admin can access
    pass

# Require specific role
@router.post("/v1/admin/users")
async def manage_users(
    current_user: User = Depends(require_admin)
):
    # Only admin can access
    pass
```

## 🚦 Rate Limiting

### Rate Limits by Role
| Role | Requests/Minute | Burst |
|------|----------------|-------|
| **admin** | 300 | 50 |
| **analyst** | 120 | 20 |
| **viewer** | 60 | 10 |

### Rate Limiting Implementation
```python
# Token bucket algorithm
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
```

### Rate Limit Headers
```http
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640997000
Retry-After: 30
```

## 🔑 Key Management

### JWT Secret Management
```bash
# Generate secure secret
openssl rand -base64 32

# Environment configuration
JWT_SECRET=$(openssl rand -base64 32)
```

### Key Rotation
1. **Generate new secret**
2. **Update environment**
3. **Restart services**
4. **Invalidate old tokens**

### Secret Storage
- **Development**: Environment variables
- **Production**: Docker secrets or external secret management
- **Never commit** secrets to version control

## 🛡️ Security Headers

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"]
)
```

### Security Headers
```python
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## 🔍 Audit Logging

### Security Events
- **Authentication**: Login attempts, token validation
- **Authorization**: Permission checks, role changes
- **Rate Limiting**: Limit exceeded events
- **API Access**: Endpoint access with user context

### Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "event": "authentication",
  "user_id": "analyst",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "success": true
}
```

### Audit Queries
```logql
# Failed authentication attempts
{job="eu-ai-act-api"} | json | event="authentication" | success=false

# Rate limit exceeded
{job="eu-ai-act-api"} | json | event="rate_limit_exceeded"

# Admin actions
{job="eu-ai-act-api"} | json | user_id="admin"
```

## 🚨 Security Monitoring

### Security Alerts
- **Failed Authentication**: Multiple failed login attempts
- **Rate Limit Abuse**: Excessive rate limit violations
- **Privilege Escalation**: Unauthorized access attempts
- **Suspicious Activity**: Unusual access patterns

### Monitoring Queries
```promql
# Failed authentication rate
rate(authentication_failures_total[5m])

# Rate limit violations
rate(rate_limit_violations_total[5m])

# Admin access frequency
rate(admin_actions_total[5m])
```

## 🔧 Security Configuration

### Environment Variables
```bash
# JWT Configuration
JWT_SECRET=your-secure-secret-key
JWT_ISSUER=eu-ai-act-api
JWT_AUDIENCE=eu-ai-act-users
JWT_EXPIRE_MINUTES=30

# User Configuration
USERS_CONFIG=admin:admin,analyst:analyst,viewer:viewer

# Security Settings
SECRET_KEY=your-application-secret
LOG_LEVEL=INFO
```

### Docker Security
```yaml
# docker-compose.yml
services:
  api:
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - SECRET_KEY=${SECRET_KEY}
    # No secrets in compose file
```

## 🛠️ Security Testing

### Authentication Testing
```bash
# Test without token (should fail)
curl -X POST http://localhost:8000/v1/answer \
  -d '{"question": "test"}'

# Test with invalid token (should fail)
curl -X POST http://localhost:8000/v1/answer \
  -H "Authorization: Bearer invalid-token" \
  -d '{"question": "test"}'

# Test with valid token (should succeed)
curl -X POST http://localhost:8000/v1/answer \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question": "test"}'
```

### Rate Limiting Testing
```bash
# Test rate limiting
for i in {1..70}; do
  curl -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/v1/answer \
    -d '{"question": "test"}' &
done
wait
```

### Authorization Testing
```bash
# Test viewer role (should fail for evaluation)
curl -X POST http://localhost:8000/v1/evaluate/offline \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -d '{"dataset_path": "test.jsonl"}'
```

## 📋 Security Checklist

### Pre-Deployment
- [ ] JWT secrets configured securely
- [ ] Rate limits appropriate for use case
- [ ] User roles and permissions defined
- [ ] Security headers configured
- [ ] Audit logging enabled

### Post-Deployment
- [ ] Monitor authentication failures
- [ ] Track rate limit violations
- [ ] Review access patterns
- [ ] Validate token expiration
- [ ] Check security logs

### Regular Maintenance
- [ ] Rotate JWT secrets
- [ ] Review user access
- [ ] Update rate limits
- [ ] Audit security logs
- [ ] Test security controls

## 🚀 Security Best Practices

### Development
1. **Never commit secrets** to version control
2. **Use environment variables** for configuration
3. **Implement proper error handling**
4. **Log security events** appropriately
5. **Test security controls** regularly

### Production
1. **Use strong secrets** (32+ characters)
2. **Implement key rotation** procedures
3. **Monitor security events** continuously
4. **Regular security audits**
5. **Incident response plan**

### Monitoring
1. **Set up security alerts**
2. **Monitor authentication patterns**
3. **Track rate limiting effectiveness**
4. **Review access logs** regularly
5. **Analyze security trends**

## 🔐 Advanced Security

### Multi-Factor Authentication
```python
# Future enhancement
class MFAProvider:
    def verify_totp(self, user_id: str, token: str) -> bool:
        # TOTP verification
        pass
```

### API Key Management
```python
# API key authentication
class APIKeyAuth:
    def verify_api_key(self, key: str) -> Optional[User]:
        # API key validation
        pass
```

### OAuth Integration
```python
# OAuth 2.0 integration
class OAuthProvider:
    def verify_oauth_token(self, token: str) -> Optional[User]:
        # OAuth token validation
        pass
```

This security guide provides comprehensive security implementation for the EU AI Act Compliance RAG System, ensuring production-ready authentication, authorization, and monitoring capabilities.