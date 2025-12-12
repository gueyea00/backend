from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models
import schemas
from auth import get_current_admin
from typing import List

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(models.User).filter(models.User.role == models.UserRole.STUDENT).count()
    total_teams = db.query(models.Team).count()
    total_documents = db.query(models.Document).count()
    pending_documents = db.query(models.Document).filter(
        models.Document.status == models.DocumentStatus.PENDING
    ).count()
    approved_documents = db.query(models.Document).filter(
        models.Document.status == models.DocumentStatus.APPROVED
    ).count()
    rejected_documents = db.query(models.Document).filter(
        models.Document.status == models.DocumentStatus.REJECTED
    ).count()
    
    return {
        "total_users": total_users,
        "total_teams": total_teams,
        "total_documents": total_documents,
        "pending_documents": pending_documents,
        "approved_documents": approved_documents,
        "rejected_documents": rejected_documents
    }

@router.get("/documents/pending", response_model=List[schemas.DocumentResponse])
def get_pending_documents(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    documents = db.query(models.Document).filter(
        models.Document.status == models.DocumentStatus.PENDING
    ).all()
    
    result = []
    for doc in documents:
        uploader = db.query(models.User).filter(models.User.id == doc.uploaded_by).first()
        result.append({
            "id": doc.id,
            "team_id": doc.team_id,
            "filename": doc.filename,
            "uploaded_by": doc.uploaded_by,
            "uploaded_at": doc.uploaded_at,
            "status": doc.status,
            "admin_comment": doc.admin_comment,
            "uploader_name": uploader.full_name if uploader else "Unknown"
        })
    
    return result

@router.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).filter(models.User.role == models.UserRole.STUDENT).all()
    return users

@router.get("/users/pending", response_model=List[schemas.UserResponse])
def get_pending_users(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).filter(
        models.User.role == models.UserRole.STUDENT,
        models.User.is_active == False
    ).all()
    return users

@router.put("/users/{user_id}/approve")
def approve_user(
    user_id: int,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    
    return {"message": "User approved successfully"}

@router.put("/teams/{team_id}/validate-sub-theme")
def validate_sub_theme(
    team_id: int,
    status: models.ValidationStatus,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    team.sub_theme_status = status
    # If REJECTED, we keep the text so they know what was rejected, but frontend should allow edit
    
    db.commit()
    
    return {"message": f"Sub-theme {status}", "status": status}
