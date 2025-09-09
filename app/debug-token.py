from jose import jwt
from config import get_settings

settings = get_settings()
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTYsInJvbGUiOiJjbGllbnQiLCJ2ZXIiOjEsImV4cCI6MTc1NzQyNzc4OSwiaWF0IjoxNzU3NDI0MTg5LCJqdGkiOiI1YmQxNGNmZi01ZmRlLTRmNjgtYTk2OS03MWE0ODExMTRkYzAiLCJ0eXBlIjoiYWNjZXNzIn0.UeUsjI4RpDP4OvhOV3T_f6ZXBpRT7s6gmjXu2DcMOGY"

try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print("Decoded payload:", payload)
except Exception as e:
    print("Failed to decode token:", repr(e))