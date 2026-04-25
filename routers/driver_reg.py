from fastapi import APIRouter, Depends, HTTPException
from Models import DriverModel
from Schema import Accounts, Driver
from database import db 
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound 
from auth import get_current_user
from Models import Role, Verification
from datetime import datetime,timezone, UTC

driver_router=APIRouter()

@driver_router.post("/driver-reg")
def driver_registration(driver:DriverModel,user:str=Depends(get_current_user),db: Session=Depends(db)):
    if Role(user["role"])== Role.USER:
        if db.query(Driver).filter(Driver.account_id==user["id"]).first():
            raise HTTPException(status_code=409,detail="The user is already registerd or applied.")
        try:
            cur_user=db.query(Accounts).filter(user["id"]==Accounts.id).one()
        except NoResultFound:
            raise HTTPException(status_code=404,detail="The user is not found.")
        except MultipleResultsFound:
            raise HTTPException(status_code=500,detail="Internal server issue.")
        new_entry=Driver(account_id=user["id"],govt_id=driver.govt_id,Vechile_Number=driver.Vechile_Number,Vechile_type=driver.Vechile_type,verification=Verification.PENDING,ver_updated_at=datetime.now(tz=UTC))
        db.add(new_entry)
        db.commit()
        return "Eureka"
    else:
       raise HTTPException(status_code=403,detail="Your role is not allowed for this operation.")
    

@driver_router.get("/all-drivers")
def all_users(db:Session=Depends(db)):
    users=db.query(Driver).all()
    return users 
    
  


    

