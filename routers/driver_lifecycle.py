from database import get_db
from  sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from Schema import Driver, porter, Accounts
from auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from enums import Status, Role
from datetime import datetime,UTC

porter_lifecycle=APIRouter()

@porter_lifecycle.patch("/driver_reached/{req_id}")
def driver_reached(req_id:int,user: str=Depends(get_current_user),db: Session=Depends(get_db)):
    if Role(user["role"])==Role.DRIVER:
        try:
            req= db.query(porter).filter(porter.id==req_id).one()
            crr_driver= db.query(Driver).filter(Driver.account_id==user["id"]).one()
        except NoResultFound:
            raise HTTPException(status_code=404,detail="Request Not found")
        except MultipleResultsFound:
            raise HTTPException(status_code=500,detail="Something went wrong.")
        if Status(req.status)== Status.ACCEPTED:
            if req.driver_id==crr_driver.id:
                req.status=Status.REACHED
                req.reached_at=datetime.now(tz=UTC).replace(tzinfo=None)
                db.commit()
                return "Reached"
            else:
                raise HTTPException(status_code=403,detail="You are not allowed to perform this action.")
        else:
            raise HTTPException(status_code=409,detail="This operation is not allowed now.")        
    else:
        raise HTTPException(status_code=403,detail="You are not allowed to preform this operation.")
    
@porter_lifecycle.patch("/driver_collected/{req_id}")
def collected(req_id:int,user: str=Depends(get_current_user),db: Session=Depends(get_db)):
    if Role(user["role"])==Role.DRIVER:
        try:
            req= db.query(porter).filter(porter.id==req_id).one()
            crr_driver= db.query(Driver).filter(Driver.account_id==user["id"]).one()
        except NoResultFound:
            raise HTTPException(status_code=404,detail="Request Not found")
        except MultipleResultsFound:
            raise HTTPException(status_code=500,detail="Something went wrong.")
        if Status(req.status)== Status.REACHED:
            if req.driver_id==crr_driver.id:
                req.status=Status.COLLECTED
                req.collected_at=datetime.now(tz=UTC).replace(tzinfo=None)
                db.commit()
                return "Collected"
            else:
                raise HTTPException(status_code=403,detail="You are not allowed to perform this action.")
        else:
            raise HTTPException(status_code=409,detail="This operation is not allowed now.")        
    else:
        raise HTTPException(status_code=403,detail="You are not allowed to preform this operation.")
    
@porter_lifecycle.patch("/driver_started/{req_id}")
def driver_started(req_id:int,user: str=Depends(get_current_user),db: Session=Depends(get_db)):
    if Role(user["role"])==Role.DRIVER:
        try:
            req= db.query(porter).filter(porter.id==req_id).one()
            crr_driver= db.query(Driver).filter(Driver.account_id==user["id"]).one()
        except NoResultFound:
            raise HTTPException(status_code=404,detail="Request Not found")
        except MultipleResultsFound:
            raise HTTPException(status_code=500,detail="Something went wrong.")
        if Status(req.status)== Status.COLLECTED:
            if req.driver_id==crr_driver.id:
                req.status=Status.STARTED
                req.started_at=datetime.now(tz=UTC).replace(tzinfo=None)
                db.commit()
                return "Started"
            else:
                raise HTTPException(status_code=403,detail="You are not allowed to perform this action.")
        else:
            raise HTTPException(status_code=409,detail="This operation is not allowed now.")        
    else:
        raise HTTPException(status_code=403,detail="You are not allowed to preform this operation.")
    

@porter_lifecycle.patch("/driver_dropped/{req_id}")
def driver_dropped(req_id:int,user: str=Depends(get_current_user),db: Session=Depends(get_db)):
    if Role(user["role"])==Role.DRIVER:
        try:
            req= db.query(porter).filter(porter.id==req_id).one()
            crr_driver= db.query(Driver).filter(Driver.account_id==user["id"]).one()
        except NoResultFound:
            raise HTTPException(status_code=404,detail="Request Not found")
        except MultipleResultsFound:
            raise HTTPException(status_code=500,detail="Something went wrong.")
        if Status(req.status)== Status.STARTED:
            if req.driver_id==crr_driver.id:
                req.status=Status.DROPPED
                req.dropped_at=datetime.now(tz=UTC).replace(tzinfo=None)
                db.commit()
                return "Dropped"
            else:
                raise HTTPException(status_code=403,detail="You are not allowed to perform this action.")
        else:
            raise HTTPException(status_code=409,detail="This operation is not allowed now.")        
    else:
        raise HTTPException(status_code=403,detail="You are not allowed to preform this operation.")
    

@porter_lifecycle.patch("/cancel_req/{req_id}")
def cancelled(req_id:int,user: str=Depends(get_current_user),db: Session=Depends(get_db)):

    if Role(user["role"])==Role.DRIVER or Role(user["role"])==Role.USER:
        try:
            req= db.query(porter).filter(porter.id==req_id).one()
            req_status=req.status
            req_driver=req.driver_id
            req_user=req.user_id
        except NoResultFound:
            raise HTTPException(status_code=404,detail="Request Not found")
        except MultipleResultsFound:
            raise HTTPException(status_code=500,detail="Something went wrong.")
        if Role(user["role"])==Role.DRIVER:
            try:
                crr_driver= db.query(Driver).filter(Driver.account_id==user["id"]).one()
                crr_driverid=crr_driver.id
            except NoResultFound:
                raise HTTPException(status_code=404,detail="Driver Not found")
            except MultipleResultsFound:
                raise HTTPException(status_code=500,detail="Something went wrong.")
            if crr_driverid== req_driver:
                if req_status== Status.ACCEPTED or req_status== Status.REACHED:
                    req.status=Status.CANCELLED
                    req.cancelled_at=datetime.now(tz=UTC).replace(tzinfo=None)
                    db.commit()
                    return "Driver cancelled"
                else:
                    raise HTTPException(status_code=409,detail="This operation is not allowed now.")
            else:
                raise HTTPException(status_code=403,detail="You are not allowed to preform this operation.")

        if Role(user["role"])==Role.USER:
            if user["id"]== req_user:
                if req_status== Status.ACCEPTED or req_status== Status.REACHED or req_status==Status.REQUESTED:
                    req.status=Status.USER_CANCELLED
                    req.user_cancelled_at=datetime.now(tz=UTC).replace(tzinfo=None)
                    db.commit()
                    return "User Cancelled"
                else:
                    raise HTTPException(status_code=409,detail="This operation is not allowed now.")
    else:
        raise HTTPException(status_code=403,detail="You are not allowed to preform this operation.")
    


