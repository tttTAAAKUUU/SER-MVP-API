"""User model - base for Customer and Provider"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from datetime import datetime
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    CUSTOMER = "CUSTOMER"
    PROVIDER = "PROVIDER"
    ADMIN = "ADMIN"


class User(Base):
    """Base user model shared by customers and providers"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
