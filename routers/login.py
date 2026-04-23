from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from Models import otp_login,otp_reg
from Schema import Accounts
from database import db, r
import secrets
from pwdlib import PasswordHash
from enums import Role
import jwt
from datetime import datetime,timezone, timedelta
from dotenv import load_dotenv
import os
load_dotenv()


login_router=APIRouter()


@login_router.post("/login")
def login(otp_model:otp_login,db:Session=Depends(db)):
    try:
        req_user=db.query(Accounts).filter(otp_model.mobnum==Accounts.mobnum).one()
    except NoResultFound:
        raise HTTPException(status_code=404,detail="The user is not found.")
    except MultipleResultsFound:
        raise HTTPException(status_code=500,detail="Internal server issue.")
    otp=''.join(str(secrets.randbelow(10)) for i in range(6))
    hashvr= PasswordHash.recommended()
    hashed_otp=hashvr.hash(otp)
    r.set(otp_model.mobnum,hashed_otp,ex=180)
    print(otp)
    return "OTP sent"

@login_router.post("/login-verify")
def login_verify(otp:otp_reg,db: Session=Depends(db)):
     hashed_otp=r.get(otp.mobnum)
     if hashed_otp is None:
         raise HTTPException(status_code=401,detail="The otp was never genrated or it expired.")
     hash_var=PasswordHash.recommended()
     if hash_var.verify(otp.otp,hashed_otp):
         try:
             data=db.query(Accounts).filter(Accounts.mobnum==otp.mobnum).one()
         except NoResultFound:
             raise HTTPException(status_code=404,detail="The user is not found.")
         except MultipleResultsFound:
             raise HTTPException(status_code=500,detail="Internal server issue.")
         payload={"id": data.id,
                  "role": Role(data.role).value,
                  "iat": datetime.now(timezone.utc),
                  "exp": datetime.now(timezone.utc)+timedelta(minutes=30),
                  "iss": "Nikhil"
                  }
         key= os.getenv("SECRET_KEY")
         encoded_tok=jwt.encode(payload=payload,key=key,algorithm="HS256")
     else:
         raise HTTPException(status_code=401,detail="The otp is wrong")

     return {"access_token": encoded_tok, "token_type": "bearer"}

    

        
    