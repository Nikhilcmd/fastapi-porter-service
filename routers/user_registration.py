from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Models import AccountModel,DriverModel,otp_reg
from Schema import Accounts, Driver, porter
from database import db, r
import secrets
from enums import Role, Gender
from pwdlib import PasswordHash
import json
from datetime import datetime,timezone


registration_router=APIRouter()

@registration_router.post("/registration")
def registration(account: AccountModel,db: Session = Depends(db)):
    if db.query(Accounts).filter(Accounts.mobnum==account.mobnum).first():
        raise HTTPException(status_code=409,detail="The user already exist.")
    if db.query(Accounts).filter(Accounts.email==account.email).first():
        raise HTTPException(status_code=409,detail="The user already exist.")
    otp = ''.join(str(secrets.randbelow(9)) for i in range(6))
    print("Registertion of user otp",otp)
    hash_var= PasswordHash.recommended()
    hashed_otp=hash_var.hash(otp)
    new_user={"name":account.name,"email":account.email,"mobnum":account.mobnum,"gender":Gender(account.gender).value,"otp":hashed_otp}
    
    # r.set(json.dump(new_user),ex=180)
    r.set(account.mobnum,json.dumps(new_user),ex=180)
    return "OTP Sent"

@registration_router.post("/register-verify")
def register_verify(otp_model:otp_reg ,db: Session=Depends(db)):
    data=r.get(otp_model.mobnum)
    if data is None:
        raise HTTPException(status_code=410,detail="The otp has expired")
    dic=json.loads(data)
    hashvar=PasswordHash.recommended()
    otp=otp_model.otp
    hash_otp=dic["otp"]
    
    if hashvar.verify(otp,hash=hash_otp):
        new_user=Accounts(name=dic["name"], email=dic["email"], role=Role.USER, gender=Gender(dic["gender"]), created_at=datetime.now(timezone.utc),mobnum=dic["mobnum"])
        db.add(new_user)
        db.commit()
        r.delete(otp_model.mobnum)
        return "coolz"
            
    else:
        raise HTTPException(status_code=401,detail="The otp was wrong.")
    
@registration_router.get("/all-users")
def all_users(db:Session=Depends(db)):
    users=db.query(Accounts).all()
    return users 

    
     


    


    

    
    


