from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from Schema import Driver, Accounts
from enums import Role, Verification
from database import get_db
from auth import get_current_user
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from datetime import datetime, timezone,UTC
from tasks import del_user
admin_router=APIRouter()

@admin_router.get("/admin/all_pending_req")
def all_req(user: str=Depends(get_current_user),db: Session=Depends(get_db)):
    if Role(user["role"])== Role.ADMIN:
        all_ver=db.query(Driver).filter(Driver.verification==Verification.PENDING).all()
        return all_ver
    else:
        raise HTTPException(status_code=403,detail="This operatio is not allowed for your role.")

@admin_router.patch("/admin_approval/{driver_id}")
def admin_approval(driver_id: int,user: str=Depends(get_current_user),db: Session=Depends(get_db)):
    if Role(user["role"])==Role.ADMIN: 
        try:
            driver_val=db.query(Driver).filter(Driver.id==driver_id).one()
            if driver_val.verification==Verification.APPROVED:
                raise HTTPException(status_code=403,detail="THe user is alredy approved.")
            if driver_val.verification==Verification.REJECTED:
                raise HTTPException(status_code=403,detail="THe user is alredy rejected.")
            acc_val=db.query(Accounts).filter(driver_val.account_id==Accounts.id).one()
        except NoResultFound:
            raise HTTPException(status_code=404,detail="This user does not exist.")
        except MultipleResultsFound:
            raise HTTPException(status_code=500,detail="Something is wrong with the system.")
        #update=driver(verification=Verification.APPROVED,ver_updated_at=datetime.now(tz=UTC))
        driver_val.verification=Verification.APPROVED
        driver_val.ver_updated_at=datetime.now(tz=UTC).replace(tzinfo=None)
        acc_val.role=Role.DRIVER
        db.commit()
        return "wow"
    else:
        raise HTTPException(status_code=403,detail="This operation is forbidden for you role.")
    
@admin_router.patch("/admin_reject/{driver_id}")
def admin_reject(driver_id:int,user: str=Depends(get_current_user),db: Session=Depends(get_db)):
    if Role(user["role"])==Role.ADMIN:
        try:
            driver_val=db.query(Driver).filter(Driver.id==driver_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404,detail="This user does not exist.")
        except MultipleResultsFound:
            raise HTTPException(status_code=500,detail="Something is wrong with the system.")
        if driver_val.verification== Verification.APPROVED:
            raise HTTPException(status_code=403,detail="The user is already Approved.")
        if driver_val.verification== Verification.REJECTED:
            raise HTTPException(status_code=403,detail="The user is already Rejected.")
        driver_val.verification=Verification.REJECTED
        driver_val.ver_updated_at=datetime.now(tz=UTC).replace(tzinfo=None)
        del_user.apply_async([driver_id],countdown=180)
        return "coolz"
        
            
    else:
        raise HTTPException(status_code=409,detail="This operation is forbidden for your role.")

        
        

        




