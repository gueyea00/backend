import sys
import os

sys.path.append(os.getcwd())

try:
    from schemas import UserCreate
    print("Imported UserCreate")
    try:
        u = UserCreate(email="test@example.com", password="password", full_name="Test User")
        print("UserCreate validation OK")
    except Exception as e:
        print(f"UserCreate validation FAILED: {e}")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
