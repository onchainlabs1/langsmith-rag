"""Security utilities and secret management."""

import os
import re
import html
import secrets
import hashlib
import time
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class SecretManager:
    """Secure secret management with encryption."""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for secrets."""
        key_file = ".secret_key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Read only for owner
            return key
    
    def encrypt_secret(self, secret: str) -> str:
        """Encrypt a secret."""
        return self.cipher.encrypt(secret.encode()).decode()
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt a secret."""
        return self.cipher.decrypt(encrypted_secret.encode()).decode()
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment with fallback."""
        return os.getenv(key, default)
    
    def validate_api_key(self, api_key: str, key_type: str) -> bool:
        """Validate API key format."""
        patterns = {
            "openai": r"^sk-proj-[a-zA-Z0-9]{48}$",
            "groq": r"^gsk_[a-zA-Z0-9]{32,}$",
            "langsmith": r"^lsv2_[a-zA-Z0-9_]{40,}$"
        }
        
        pattern = patterns.get(key_type)
        if not pattern:
            return False
            
        return bool(re.match(pattern, api_key))


class InputValidator:
    """Input validation and sanitization."""
    
    def __init__(self):
        self.max_question_length = 1000
        self.min_question_length = 10
        self.suspicious_patterns = [
            r'ignore\s+previous\s+instructions',
            r'system\s+prompt',
            r'role\s*:\s*assistant',
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*='
        ]
    
    def validate_question(self, question: str) -> Dict[str, Any]:
        """Validate and sanitize user question."""
        result = {
            "valid": True,
            "sanitized": question,
            "warnings": [],
            "errors": []
        }
        
        # Length validation
        if len(question) < self.min_question_length:
            result["valid"] = False
            result["errors"].append(f"Question too short (min {self.min_question_length} chars)")
        
        if len(question) > self.max_question_length:
            result["valid"] = False
            result["errors"].append(f"Question too long (max {self.max_question_length} chars)")
        
        # HTML sanitization
        sanitized = html.escape(question)
        if sanitized != question:
            result["warnings"].append("HTML characters escaped")
            result["sanitized"] = sanitized
        
        # Suspicious pattern detection
        for pattern in self.suspicious_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                result["valid"] = False
                result["errors"].append("Suspicious content detected")
                break
        
        # SQL injection patterns
        sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                result["warnings"].append("Potential SQL injection pattern detected")
        
        return result
    
    def sanitize_for_logging(self, text: str) -> str:
        """Sanitize text for safe logging."""
        # Remove potential PII
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
        text = re.sub(r'\b\d{4}-\d{4}-\d{4}-\d{4}\b', '[CARD_REDACTED]', text)
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', text)
        
        # Truncate long text
        if len(text) > 200:
            text = text[:200] + "...[TRUNCATED]"
        
        return text


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers for responses."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


class RateLimiter:
    """Enhanced rate limiting with security features."""
    
    def __init__(self):
        self.requests = {}  # In production, use Redis
        self.blocked_ips = set()
        self.suspicious_ips = {}
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        return ip in self.blocked_ips
    
    def record_suspicious_activity(self, ip: str, reason: str):
        """Record suspicious activity."""
        if ip not in self.suspicious_ips:
            self.suspicious_ips[ip] = []
        
        self.suspicious_ips[ip].append({
            "timestamp": time.time(),
            "reason": reason
        })
        
        # Block IP after 5 suspicious activities
        if len(self.suspicious_ips[ip]) >= 5:
            self.blocked_ips.add(ip)
            logger.warning(f"IP {ip} blocked due to suspicious activity")
    
    def check_rate_limit(self, ip: str, user_id: str = None) -> Dict[str, Any]:
        """Check rate limit with security monitoring."""
        current_time = time.time()
        
        # Check if IP is blocked
        if self.is_ip_blocked(ip):
            return {
                "allowed": False,
                "reason": "IP blocked",
                "retry_after": 3600
            }
        
        # Simple rate limiting (in production, use Redis)
        key = f"{ip}:{user_id or 'anonymous'}"
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if current_time - req_time < 60  # 1 minute window
        ]
        
        # Check limit
        if len(self.requests[key]) >= 60:  # 60 requests per minute
            self.record_suspicious_activity(ip, "Rate limit exceeded")
            return {
                "allowed": False,
                "reason": "Rate limit exceeded",
                "retry_after": 60
            }
        
        # Record request
        self.requests[key].append(current_time)
        
        return {
            "allowed": True,
            "remaining": 60 - len(self.requests[key])
        }


# Global instances
secret_manager = SecretManager()
input_validator = InputValidator()
security_headers = SecurityHeaders()
rate_limiter = RateLimiter()
