from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models
import schemas
from auth import get_current_user, get_current_admin
from typing import List
import random
from datetime import datetime

router = APIRouter(prefix="/api/teams", tags=["Teams"])

THEMES = ["Élevage", "Agriculture", "Pêche"]

@router.post("/create", response_model=dict)
def create_teams(current_admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    # Check if teams already exist
    existing_teams = db.query(models.Team).count()
    if existing_teams > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teams already created. Delete existing teams first."
        )
    
    # Create 3 teams with empty themes
    teams_created = []
    for i in range(1, 4):
        team = models.Team(
            name=f"Équipe {i}",
            theme=None,  # Theme assigned later via draw
            logo_url="/uploads/logos/team_1_smile.gif"
        )
        db.add(team)
        teams_created.append(team)
    
    db.commit()
    
    return {
        "message": "Teams created successfully. Students must be assigned manually.",
        "teams": [{"id": t.id, "name": t.name, "theme": t.theme} for t in teams_created],
        "students_assigned": 0
    }

@router.get("", response_model=List[schemas.TeamResponse])
def get_all_teams(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    teams = db.query(models.Team).all()
    
    # Add member count
    result = []
    for team in teams:
        member_count = db.query(models.User).filter(models.User.team_id == team.id).count()
        team_dict = {
            "id": team.id,
            "name": team.name,
            "theme": team.theme,
            "sub_theme": team.sub_theme,
            "sub_theme_status": team.sub_theme_status,
            "logo_url": team.logo_url or "/uploads/logos/team_1_smile.gif",
            "created_at": team.created_at,
            "status": team.status,
            "member_count": member_count
        }
        result.append(team_dict)
    
    return result

@router.get("/my-team", response_model=schemas.TeamDetail)
def get_my_team(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not assigned to any team yet"
        )
    
    team = db.query(models.Team).filter(models.Team.id == current_user.team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if not team.logo_url:
        team.logo_url = "/uploads/logos/team_1_smile.gif"

    return team

@router.get("/{team_id}", response_model=schemas.TeamDetail)
def get_team_by_id(team_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if not team.logo_url:
        team.logo_url = "/uploads/logos/team_1_smile.gif"

    return team

@router.post("/{team_id}/assign/{user_id}")
def assign_member(
    team_id: int, 
    user_id: int, 
    current_admin: models.User = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.team_id:
        raise HTTPException(status_code=400, detail="User already in a team")
        
    user.team_id = team_id
    db.commit()
    
    return {"message": "User assigned successfully"}

@router.post("/draw-theme")
def draw_theme(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        raise HTTPException(status_code=400, detail="User not in a team")
        
    team = db.query(models.Team).filter(models.Team.id == current_user.team_id).first()
    if team.theme:
        raise HTTPException(status_code=400, detail="Team already has a theme")
        
    # Get used themes
    used_themes = [t.theme for t in db.query(models.Team).filter(models.Team.theme != None).all()]
    available_themes = [t for t in THEMES if t not in used_themes]
    
    if not available_themes:
        raise HTTPException(status_code=400, detail="No themes available")
        
    # Randomly pick
    selected_theme = random.choice(available_themes)
    team.theme = selected_theme
    db.commit()
    
    return {"theme": selected_theme}

@router.put("/rename")
def rename_team(
    new_name: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        raise HTTPException(status_code=400, detail="User not in a team")
        
    team = db.query(models.Team).filter(models.Team.id == current_user.team_id).first()
    
    # Check uniqueness
    existing = db.query(models.Team).filter(models.Team.name == new_name).first()
    if existing and existing.id != team.id:
        raise HTTPException(status_code=400, detail="Team name already taken")
        
    team.name = new_name
    db.commit()
    
    return {"message": "Team renamed successfully", "name": new_name}

@router.put("/sub-theme")
def set_sub_theme(
    sub_theme: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        raise HTTPException(status_code=400, detail="User not in a team")
        
    team = db.query(models.Team).filter(models.Team.id == current_user.team_id).first()
    
    if not team.theme:
         raise HTTPException(status_code=400, detail="Team must have a main theme first")
         
    today = datetime.utcnow()
    
    # Optional: Log the change history if needed
    
    team.sub_theme = sub_theme
    team.sub_theme_status = models.ValidationStatus.PENDING
    db.commit()
    
    return {"message": "Sub-theme set successfully. Awaiting admin approval.", "sub_theme": sub_theme, "status": "pending"}

from fastapi import File, UploadFile
import shutil
import os

@router.post("/logo")
def upload_team_logo(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        raise HTTPException(status_code=400, detail="User not in a team")
        
    team = db.query(models.Team).filter(models.Team.id == current_user.team_id).first()
    
    # Ensure upload dir exists
    UPLOAD_DIR = "uploads/logos"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    filename = f"team_{team.id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update DB - store relative path
    relative_path = f"/uploads/logos/{filename}"
    team.logo_url = relative_path
    db.commit()
    
    return {"logo_url": relative_path}
