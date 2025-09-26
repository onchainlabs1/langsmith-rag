"""Simple tests that don't require API keys."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_security_module():
    """Test that security module can be imported."""
    try:
        import src.core.security
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import src.core.security: {e}")


def test_auth_module():
    """Test that auth module can be imported."""
    try:
        import src.core.auth
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import src.core.auth: {e}")


def test_observability():
    """Test that observability module can be imported."""
    try:
        import src.core.observability
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import src.core.observability: {e}")


def test_security_validation():
    """Test security validation functions."""
    try:
        from src.core.security import input_validator
        
        # Test valid input
        result = input_validator.validate_question("What is the EU AI Act?")
        assert result["valid"] is True
        
        # Test invalid input (too short)
        result = input_validator.validate_question("Hi")
        assert result["valid"] is False
        
    except Exception as e:
        pytest.fail(f"Security validation test failed: {e}")


def test_rate_limiter():
    """Test rate limiter functionality."""
    try:
        from src.core.security import rate_limiter
        
        # Test rate limiting
        result = rate_limiter.check_rate_limit("127.0.0.1", "test_user")
        assert "allowed" in result
        
    except Exception as e:
        pytest.fail(f"Rate limiter test failed: {e}")


def test_secret_manager():
    """Test secret manager functionality."""
    try:
        from src.core.security import secret_manager
        
        # Test getting a secret
        secret = secret_manager.get_secret("TEST_SECRET", "default_value")
        assert secret == "default_value"
        
    except Exception as e:
        pytest.fail(f"Secret manager test failed: {e}")


def test_input_sanitization():
    """Test input sanitization."""
    try:
        from src.core.security import input_validator
        
        # Test HTML sanitization
        result = input_validator.validate_question("<script>alert('xss')</script>What is the EU AI Act?")
        assert result["valid"] is False
        
        # Test SQL injection patterns
        result = input_validator.validate_question("SELECT * FROM users WHERE id = 1")
        assert "warnings" in result
        
    except Exception as e:
        pytest.fail(f"Input sanitization test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
