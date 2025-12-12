import cryptography
print(f"Cryptography version: {cryptography.__version__}")
try:
    from jose import jwt
    print("Imported jose.jwt")
    token = jwt.encode({"sub": "test"}, "secret", algorithm="HS256")
    print(f"Token encoded: {token}")
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    print(f"Token decoded: {decoded}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
