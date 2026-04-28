from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from  Schema import porter
from enums import Role, Status
from sqlalchemy.orm import Session
from auth import get_current_user
from datetime import datetime, timezone,UTC

from Models import porterModel

porter_req=APIRouter()

@porter_req.post("/req-porter")
def porter_request(porter_model: porterModel,user: str=Depends(get_current_user),db: Session=Depends(get_db)):
    if Role(user["role"])!=Role.ADMIN:
        new_req=porter(user_id=user["id"],status=Status.REQUESTED,pickup_loc=porter_model.pickup_loc,drop_loc=porter_model.drop_loc,requested_at=datetime.now(UTC),pickup_loc_long=porter_model.pickup_loc_long,pickup_loc_lat=porter_model.pickup_loc_lat,drop_loc_long=porter_model.drop_loc_long,drop_loc_lat=porter_model.drop_loc_lat)
        db.add(new_req)
        db.commit()
    else:
        raise HTTPException(status_code=403,detail="Requesting dervice is only allowed by users.")
    return "cool"

@porter_req.get("/all_request")
def show_req(db: Session=Depends(get_db)):
    all_req=db.query(porter).all()
    return all_req


