from celery import Celery
from dotenv import load_dotenv
from Schema import Driver, porter
from database import Sessionlocal, r
from enums import Status
from datetime import datetime, UTC, timedelta

import os
load_dotenv()

app=Celery('task',broker=os.getenv("CELERY_URL"))


@app.task
def del_user(driver_id):
    session = Sessionlocal()
    try:
       element=session.query(Driver).filter(Driver.id==driver_id).one_or_none()
       if element is None:
        return "no user found"
       session.delete(element)
       session.commit()
    finally:
        session.close() 

@app.task(bind=True)
def radius_expansion(self,request_id):
   session = Sessionlocal()
   
   try:
       element=session.query(porter).filter(porter.id==request_id).one_or_none()
       if element is None:
        return "Something went wrong"
       if Status(element.status)!=Status.REQUESTED:
          return "This ride is already accepted."
       diffrence=datetime.now(tz=UTC).replace(tzinfo=None)-element.requested_at
       print(element.requested_at)
       print("This is the diffrence",diffrence)
       if diffrence > timedelta(seconds=600):
          print("diffrence is what the hell ", diffrence.total_seconds())
          element.status=Status.CANCELLED
          element.cancelled_at=datetime.now(tz=UTC)
          session.commit()
          return "This ride is cancelled as no driver found."
       ride_lat=element.pickup_loc_lat
       ride_long=element.pickup_loc_long
       n=r.incr(f"radius:{request_id}",amount=1)
       
       vri=r.geosearch("driver_location",None,ride_long,ride_lat,"km",min(n+1,9),sort="ASC",withdist=True)
       
       
       print(vri)
       print("This is the radius",min(n+1,9))

       for t in vri:
          if r.get(f"driver_online:{t[0]}") is not None:
             print("this is", t[0])
             r.zadd(f"eligible_drivers:{request_id}",{t[0]:t[1]},nx=True)
       r.expire(f"eligible_drivers:{request_id}",time=60)
       radius_expansion.apply_async([request_id],countdown=30)
             
   finally:
      session.close()