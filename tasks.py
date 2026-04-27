from celery import Celery
from dotenv import load_dotenv
from Schema import Driver
from database import Sessionlocal

import os
load_dotenv()

app=Celery('task',broker=os.getenv("CELERY_URL"))


@app.task
def del_user(driver_id):
    session = Sessionlocal()
    try:
       element=session.query(Driver).filter(Driver.id==driver_id).one_or_none()
       if element is None:
        session.delete(element)
        session.commit()
    finally:
        session.close() 
