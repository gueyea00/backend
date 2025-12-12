import sys
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import schemas
from auth import get_password_hash, create_access_token

sys.path.append(os.getcwd())

def test_register():
    print("Testing register flow...")
    db = SessionLocal()
    try:
        user_data = schemas.UserCreate(
            email="newuser2@test.com", 
            password="password123", 
            full_name="New Test User"
        )
        
        # Check if user exists (should not, hopefully)
        existing = db.query(models.User).filter(models.User.email == user_data.email).first()
        if existing:
            print("User already exists, skipping create")
        else:
            new_user = models.User(
                email=user_data.email,
                password_hash=get_password_hash(user_data.password),
                full_name=user_data.full_name,
                role=models.UserRole.STUDENT
            )
            print("Adding user to session...")
            db.add(new_user)
            print("Committing...")
            db.commit()
            print("Refreshing...")
            db.refresh(new_user)
            print(f"User created with ID: {new_user.id}")

            print("Creating token...")
            token = create_access_token(data={"sub": str(new_user.id)})
            print(f"Token: {token}")

    except Exception as e:
        print(f"CRASH during register: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_register()
