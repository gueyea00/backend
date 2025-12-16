from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import UserRole, DocumentStatus, TeamStatus

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    admin_code: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    team_id: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

# Team Schemas
class TeamBase(BaseModel):
    name: str
    theme: Optional[str] = None
    sub_theme: Optional[str] = None
    sub_theme_status: Optional[str] = None
    logo_url: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    status: TeamStatus
    member_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class TeamDetail(TeamResponse):
    members: List[UserResponse]
    
    class Config:
        from_attributes = True

# Document Schemas
class DocumentBase(BaseModel):
    filename: str

class DocumentUpload(BaseModel):
    pass

class DocumentResponse(DocumentBase):
    id: int
    team_id: int
    uploaded_by: int
    uploaded_at: datetime
    status: DocumentStatus
    admin_comment: Optional[str]
    uploader_name: Optional[str]
    
    class Config:
        from_attributes = True

class DocumentValidation(BaseModel):
    status: DocumentStatus
    admin_comment: Optional[str] = None

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_users: int
    total_teams: int
    total_documents: int
    pending_documents: int
    approved_documents: int
    rejected_documents: int
