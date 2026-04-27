from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from fastapi import Depends
import jwt
import os
from dotenv import load_dotenv
load_dotenv()

oauth=OAuth2PasswordBearer(tokenUrl="/login-verify")

def get_current_user(token: str=Depends(oauth)):
    try:
     decode=jwt.decode(token,os.getenv("SECRET_KEY"),algorithms=["HS256"])
     return decode
    except jwt.exceptions.ExpiredSignatureError:
       raise HTTPException(status_code=401,detail="Token Expired")
    except jwt.exceptions.ImmatureSignatureError:
       raise HTTPException(status_code=401,detail="Invalid token")
