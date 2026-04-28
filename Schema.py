from sqlalchemy.orm import declarative_base
from sqlalchemy import Column,Integer,String, Enum, Float, DateTime,ForeignKey

from enums import Gender,Role,Verification, Status, Vechile_type
Base= declarative_base()

class Accounts(Base):
    __tablename__="Accounts_table"
    id=Column(Integer,unique=True,primary_key=True)
    name=Column(String(50))
    email=Column(String(50),unique=True)
    mobnum=Column(String(50),unique=True)
    gender=Column(Enum(Gender))
    role=Column(Enum(Role))
    created_at=Column(DateTime)

class Driver(Base):
    __tablename__="Driver_table"
    id=Column(Integer,unique=True,primary_key=True)
    account_id=Column(ForeignKey(Accounts.id),unique=True)
    govt_id=Column(String(50))
    Vechile_Number=Column(String(50),unique=True)
    Vechile_type=Column(Enum(Vechile_type))
    verification=Column(Enum(Verification))
    ver_updated_at=Column(DateTime)

class porter(Base):
    __tablename__="porter_table"
    id=Column(Integer,primary_key=True)
    driver_id=Column(ForeignKey(Driver.id))
    user_id=Column(ForeignKey(Accounts.id))
    status=Column(Enum(Status))
    pickup_loc=Column(String(50))
    pickup_loc_long=Column(Float)
    pickup_loc_lat=Column(Float)
    drop_loc=Column(String(50))
    drop_loc_long=Column(Float)
    drop_loc_lat=Column(Float)
    requested_at=Column(DateTime)
    accepted_at=Column(DateTime)
    collected_at=Column(DateTime)
    started_at=Column(DateTime)
    reached_at=Column(DateTime)
    dropped_at=Column(DateTime)
    cancelled_at= Column(DateTime)
    user_cancelled_at= Column(DateTime)