import sys
import os
import traceback

sys.path.append(os.getcwd())

with open("error_log.txt", "w") as f:
    try:
        from auth import get_password_hash
        print("Imported auth", file=f)
        
        pwd = "password123"
        print(f"Hashing {pwd}", file=f)
        h = get_password_hash(pwd)
        print(f"Hashed: {h}", file=f)
        
    except Exception:
        traceback.print_exc(file=f)
