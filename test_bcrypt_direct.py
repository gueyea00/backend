import bcrypt

print("Imported bcrypt")
pwd = b"password123"
hashed = bcrypt.hashpw(pwd, bcrypt.gensalt())
print(f"Hashed: {hashed}")
check = bcrypt.checkpw(pwd, hashed)
print(f"Check: {check}")
