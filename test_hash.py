from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print("Testing bytes:")
try:
    # Mimic what is in auth.py
    pwd_bytes = "password123".encode('utf-8')[:72]
    res = pwd_context.hash(pwd_bytes)
    print(f"Bytes success: {res[:10]}...")
except Exception as e:
    print(f"Bytes failed: {e}")

print("\nTesting string:")
try:
    res = pwd_context.hash("password123")
    print(f"String success: {res[:10]}...")
except Exception as e:
    print(f"String failed: {e}")
