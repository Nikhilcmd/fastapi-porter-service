from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import session, Session
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from Schema import  porter, Driver
from database import get_db, r
from enums import Role, Status
from auth import get_current_user
from datetime import datetime, timezone,UTC

porter_accept=APIRouter()

@porter_accept.patch("/accept-porter/{req_id}")
def accept(req_id:int,user: str=Depends(get_current_user),db:Session=Depends(get_db)):
    if Role(user["role"])== Role.DRIVER:
        try:
            driver=db.query(Driver).filter(Driver.account_id==user["id"]).one()
            driver_eligible=db.query(porter).filter(porter.driver_id==driver.id, or_(porter.status==Status.ACCEPTED , porter.status==Status.STARTED, porter.status==Status.COLLECTED,porter.status==Status.REACHED)).one_or_none()
            # print(r.get(f"eligible_drivers:{req_id}"))
            if str(driver.account_id) not  in r.zrange(f"eligible_drivers:{req_id}",start=0,end=-1):
                raise HTTPException(status_code=403,detail="You are not allowed to accept this request. distance")

            if driver_eligible != None:
                raise HTTPException(status_code=403,detail="You are not allowed to take up this request.")
            req=db.query(porter).filter(req_id==porter.id).with_for_update().one()
            
        except NoResultFound:
            raise HTTPException(status_code=404,detail="The request is not found.")
        except MultipleResultsFound:
            raise HTTPException(status_code=500,detail="Internal Server issue.")
        
        
        
            
        if Status(req.status)== Status.REQUESTED:
            req.driver_id=driver.id
            req.status=Status.ACCEPTED
            req.accepted_at=datetime.now(tz=UTC).replace(tzinfo=None)
            db.commit()
            return "Accepted wow"
        else:
            raise HTTPException(status_code=409,detail="This request can not be accepted.")

        


    else:
        raise HTTPException(status_code=403,detail="This operation is not allowed by your role.")
