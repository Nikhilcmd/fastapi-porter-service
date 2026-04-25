from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
import jwt
import os
from dotenv import load_dotenv
load_dotenv()

oauth=OAuth2PasswordBearer(tokenUrl="/login-verify")

def get_current_user(token: str=Depends(oauth)):
    decode=jwt.decode(token,os.getenv("SECRET_KEY"),algorithms=["HS256"])
    return decode
