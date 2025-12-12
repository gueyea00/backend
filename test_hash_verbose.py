import traceback
import sys

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    print("Context created")
    
    pwd = "password123"
    print(f"Hashing '{pwd}'")
    
    # 1. Try raw string
    try:
        h = pwd_context.hash(pwd)
        print("Raw string hash OK")
    except:
        print("Raw string hash FAILED")
        traceback.print_exc()

    # 2. Try bytes
    try:
        b = pwd.encode('utf-8')[:72]
        print(f"Hashing bytes: {b}")
        h = pwd_context.hash(b)
        print("Bytes hash OK")
    except:
        print("Bytes hash FAILED")
        traceback.print_exc()

except:
    traceback.print_exc()
