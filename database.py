from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()
import os
import redis
r=redis.Redis('localhost',port=6379,decode_responses=True)
from sqlalchemy.orm import sessionmaker
engine=create_engine(os.getenv("DATABASE_URL"))


Sessionlocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

def db():
    session=Sessionlocal()
    yield session

    session.close()












