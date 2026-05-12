from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()
import os
import redis
import redis.asyncio as aredis
r=redis.Redis(os.getenv("REDIS_HOST_NAME"),port=6379,decode_responses=True)
ar=aredis.Redis(host=os.getenv("REDIS_HOST_NAME"),port=6379,decode_responses=True)

from sqlalchemy.orm import sessionmaker
engine=create_engine(os.getenv("DATABASE_URL"))


Sessionlocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

def get_db():
    session=Sessionlocal()
    try:
     yield session
    finally:
       session.close()












