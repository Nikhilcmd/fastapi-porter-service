from celery import Celery
from dotenv import load_dotenv
from Schema import Driver, porter
from database import Sessionlocal, r
from enums import Status
from datetime import datetime, UTC, timedelta
from redis.exceptions import TimeoutError, ConnectionError, ResponseError
import os
import logging
load_dotenv()

logger=logging.getLogger("tasks")
logging.basicConfig(level=logging.DEBUG)

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
   p=r.pipeline(transaction=False)
   
   try:
       element=session.query(porter).filter(porter.id==request_id).one_or_none()
       if element is None:
        return "Something went wrong"
       if element.status!=Status.REQUESTED:
          return "This ride is already accepted or cancelled."
       diffrence=datetime.now(tz=UTC).replace(tzinfo=None)-element.requested_at
       logger.debug(element.requested_at)
       logger.debug(f"This is the diffrence{diffrence}")

       if diffrence > timedelta(seconds=600):
          logger.debug(f"diffrence is what the hell {diffrence.total_seconds()}")
          element.status=Status.CANCELLED
          element.cancelled_at=datetime.now(tz=UTC)
          session.commit()
          return "This ride is cancelled as no driver found."
       cords=[]
       ride_lat=element.pickup_loc_lat
       ride_long=element.pickup_loc_long
       try:
         n=r.incr(f"radius:{request_id}",amount=1)
         r.expire(f"radius:{request_id}",time=1020,nx=True)
         
         vri=r.geosearch("driver_location",None,ride_long,ride_lat,"km",min(n+1,9),sort="ASC",withdist=True)
         
      
         
      
         logger.debug(f"why are these here{vri}")
         logger.debug(f"This is the radius{min(n+1,9)}")
         for t in vri:
            p.get(f"driver_online:{t[0]}")
            cords.append(t[1])

         driverid=p.execute()
         logger.debug(type(driverid))


         for driverid, cords in zip(driverid, cords):
            logger.debug(f"this is{driverid}:{cords}")
            if driverid is not None:
               r.zadd(f"eligible_drivers:{request_id}",{driverid:cords},nx=True)
         r.expire(f"eligible_drivers:{request_id}",time=60)
         radius_expansion.apply_async([request_id],countdown=30)
       except TimeoutError as e:
          logger.debug("The Redis operation timed out")
          raise self.retry(exc=e, countdown=10)
       except ConnectionError as e:
          logger.debug("Could not connect to Redis. Retry intiated.")
          raise self.retry(exc=e, countdown=10)
       except ResponseError as e:
          logger.debug(f"Redis command error: {e}")
          raise self.retry(exc=e, countdown=10)
          
                  
   finally:
      session.close()