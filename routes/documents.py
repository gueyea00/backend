from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth import get_current_user, get_current_admin
from typing import List
import os
import shutil
from datetime import datetime

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = [".ppt", ".pptx", ".doc", ".docx", ".pdf"]

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user has a team
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be assigned to a team to upload documents"
        )
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024} MB"
        )
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"team{current_user.team_id}_{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create database record
    document = models.Document(
        team_id=current_user.team_id,
        filename=file.filename,
        file_path=file_path,
        uploaded_by=current_user.id
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return {
        "id": document.id,
        "team_id": document.team_id,
        "filename": document.filename,
        "uploaded_by": document.uploaded_by,
        "uploaded_at": document.uploaded_at,
        "status": document.status,
        "admin_comment": document.admin_comment,
        "uploader_name": current_user.full_name
    }

@router.get("/team/{team_id}", response_model=List[schemas.DocumentResponse])
def get_team_documents(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Students can only see their own team's documents
    if current_user.role == models.UserRole.STUDENT and current_user.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own team's documents"
        )
    
    documents = db.query(models.Document).filter(models.Document.team_id == team_id).all()
    
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

@router.get("/my-documents", response_model=List[schemas.DocumentResponse])
def get_my_documents(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        return []
    
    return get_team_documents(current_user.team_id, db, current_user)

@router.put("/{doc_id}/validate", response_model=schemas.DocumentResponse)
def validate_document(
    doc_id: int,
    validation: schemas.DocumentValidation,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document.status = validation.status
    document.admin_comment = validation.admin_comment
    
    db.commit()
    db.refresh(document)
    
    uploader = db.query(models.User).filter(models.User.id == document.uploaded_by).first()
    
    return {
        "id": document.id,
        "team_id": document.team_id,
        "filename": document.filename,
        "uploaded_by": document.uploaded_by,
        "uploaded_at": document.uploaded_at,
        "status": document.status,
        "admin_comment": document.admin_comment,
        "uploader_name": uploader.full_name if uploader else "Unknown"
    }

@router.get("/{doc_id}/download")
def download_document(
    doc_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check permissions
    if current_user.role == models.UserRole.STUDENT and current_user.team_id != document.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only download your own team's documents"
        )
    
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    return FileResponse(
        path=document.file_path,
        filename=document.filename,
        media_type="application/octet-stream"
    )
