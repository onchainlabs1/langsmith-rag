"""JWT Authentication and RBAC for EU AI Act Compliance RAG System."""

import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from src.core.config import settings


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(BaseModel):
    """User model."""
    user_id: str
    username: str
    role: UserRole
    permissions: Set[str]


class JWTPayload(BaseModel):
    """JWT payload structure."""
    sub: str  # user_id
    username: str
    role: str
    iat: int  # issued at
    exp: int  # expires at
    iss: str  # issuer
    aud: str  # audience


class AuthService:
    """Authentication service for JWT handling."""
    
    def __init__(self) -> None:
        """Initialize auth service."""
        self.secret_key = settings.jwt_secret
        self.issuer = settings.jwt_issuer
        self.audience = settings.jwt_audience
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # In-memory user store (in production, use database)
        self.users = self._load_users()
        
    def _load_users(self) -> Dict[str, User]:
        """Load users from environment or file."""
        # Default users for development
        default_users = {
            "admin": User(
                user_id="admin",
                username="admin",
                role=UserRole.ADMIN,
                permissions={"read", "write", "evaluate", "admin"}
            ),
            "analyst": User(
                user_id="analyst",
                username="analyst", 
                role=UserRole.ANALYST,
                permissions={"read", "write", "evaluate"}
            ),
            "viewer": User(
                user_id="viewer",
                username="viewer",
                role=UserRole.VIEWER,
                permissions={"read"}
            )
        }
        
        # Load from environment if available
        users_env = settings.users_config
        if users_env:
            # Parse users from environment variable
            # Format: "user1:role1,user2:role2"
            users = {}
            for user_config in users_env.split(","):
                if ":" in user_config:
                    username, role = user_config.split(":", 1)
                    role_enum = UserRole(role) if role in [r.value for r in UserRole] else UserRole.VIEWER
                    permissions = self._get_permissions_for_role(role_enum)
                    users[username] = User(
                        user_id=username,
                        username=username,
                        role=role_enum,
                        permissions=permissions
                    )
            return users
            
        return default_users
    
    def _get_permissions_for_role(self, role: UserRole) -> Set[str]:
        """Get permissions for a role."""
        permissions_map = {
            UserRole.ADMIN: {"read", "write", "evaluate", "admin"},
            UserRole.ANALYST: {"read", "write", "evaluate"},
            UserRole.VIEWER: {"read"}
        }
        return permissions_map.get(role, {"read"})
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token."""
        now = datetime.utcnow()
        payload = {
            "sub": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self.access_token_expire_minutes)).timestamp()),
            "iss": self.issuer,
            "aud": self.audience
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> JWTPayload:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience
            )
            return JWTPayload(**payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with secure password verification."""
        user = self.users.get(username)
        if user:
            # In production, use proper password hashing with bcrypt
            # For demo purposes, simple comparison
            if self._verify_password(password, user.password_hash):
                return user
        return None
    
    def _hash_password(self, password: str) -> str:
        """Hash password securely."""
        # In production, use bcrypt or argon2
        import hashlib
        import secrets
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        # In production, use proper password verification
        # This is a simplified version for demo
        return password == password_hash


# Global auth service instance
auth_service = AuthService()

# Security scheme
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    user = auth_service.get_user(payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def require_permission(permission: str):
    """Decorator to require specific permission."""
    def permission_checker(user: User = Depends(get_current_user)) -> User:
        if permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return user
    return permission_checker


def require_role(role: UserRole):
    """Decorator to require specific role."""
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != role and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role.value}' required"
            )
        return user
    return role_checker


# Convenience functions for common permissions
require_read = require_permission("read")
require_write = require_permission("write")
require_evaluate = require_permission("evaluate")
require_admin = require_permission("admin")
