import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from auth import get_password_hash, create_access_token, verify_password
    from database import SessionLocal, engine
    from models import Base, User
    from sqlalchemy import text
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

print("1. Testing Password Hashing...")
try:
    pwd = "testpassword"
    hashed = get_password_hash(pwd)
    print(f"   Hash generated: {hashed[:10]}...")
    assert verify_password(pwd, hashed)
    print("   Password hashing OK")
except Exception as e:
    print(f"   Error in password hashing: {e}")
    import traceback
    traceback.print_exc()

print("\n2. Testing JWT Token Creation...")
try:
    token = create_access_token({"sub": "1"})
    print(f"   Token generated: {token[:10]}...")
    print("   JWT Token OK")
except Exception as e:
    print(f"   Error in JWT: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Testing Database Connection...")
try:
    db = SessionLocal()
    # Try a simple query
    db.execute(text("SELECT 1"))
    print("   Database connection OK")
    
    # Check users table
    try:
        users = db.query(User).limit(5).all()
        print(f"   Found {len(users)} users.")
    except Exception as e:
        print(f"   Error querying users: {e}")
    db.close()
except Exception as e:
    print(f"   Error in DB: {e}")
    import traceback
    traceback.print_exc()
