from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"

class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class TeamStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"

class ValidationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    is_active = Column(Boolean, default=True)  # Defaults to True to support old users, logic handles False for new
    created_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team", back_populates="members")
    uploaded_documents = relationship("Document", back_populates="uploader")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    theme = Column(String, nullable=True)  # Initially null, set via draw
    sub_theme = Column(String, nullable=True)  # Defined by students
    sub_theme_status = Column(Enum(ValidationStatus), nullable=True)
    logo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(TeamStatus), default=TeamStatus.ACTIVE)
    
    members = relationship("User", back_populates="team")
    documents = relationship("Document", back_populates="team")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    admin_comment = Column(String, nullable=True)
    
    team = relationship("Team", back_populates="documents")
    uploader = relationship("User", back_populates="uploaded_documents")
