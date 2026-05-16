import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from Schema import Base
from main import app
from database import get_db, r
from fastapi.testclient import TestClient
from Schema import Accounts, Driver, porter
from enums import Role, Gender, Vechile_type, Verification, Status
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import Depends, HTTPException
from unittest.mock import patch






load_dotenv()
Testengine=create_engine(os.getenv("TEST_DATABASE_URL"))


TestSessionlocal=sessionmaker(autoflush=False,autocommit=False,bind=Testengine)
Base.metadata.create_all(bind=Testengine)
def get_test_db():
    db=TestSessionlocal()
    try:
     yield db
    finally:
       db.close()

@pytest.fixture
def db_session():
    db = TestSessionlocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_client():
   app.dependency_overrides[get_db]=get_test_db
   db = TestSessionlocal()
   client = TestClient(app)
   Base.metadata.create_all(Testengine)
   testuser1=Accounts(name="testuser1",email="testuser1",mobnum="9876543210",gender=Gender.MALE,role=Role.USER,created_at=datetime.now(timezone.utc).isoformat())
   testadmin=Accounts(name="testadmin",email="testadmin",mobnum="9876543211",gender=Gender.MALE,role=Role.ADMIN,created_at=datetime.now(timezone.utc).isoformat())
   testdriver1=Accounts(name="testdriver1",email="testdriver1",mobnum="9876543212",gender=Gender.MALE,role=Role.DRIVER,created_at=datetime.now(timezone.utc).isoformat())
   db.add(testuser1)
   db.add(testadmin)
   db.add(testdriver1)
   db.commit()
   testdriver=Driver(account_id=testdriver1.id,govt_id="random",Vechile_Number="random",Vechile_type=Vechile_type.ELECTRIC,verification=Verification.APPROVED)
   db.add(testdriver)
   db.commit()
   yield client

   Base.metadata.drop_all(Testengine)
   app.dependency_overrides = {}


@pytest.fixture
def test_user_login(test_client):
   data={"mobnum": "9876543210"}
   response=test_client.post("/login",json=data)
   
   otp=response.json()

   
   data2={"mobnum": "9876543210",
          "otp": otp}
   response2=test_client.post("/login-verify",json=data2)
#    assert response.status_code==200
#    assert response2.status_code==200
   return response2.json()["access_token"]

@pytest.fixture
def test_driver_login(test_client):
   data={"mobnum": "9876543212"}
   response=test_client.post("/login",json=data)
   
   otp=response.json()

   
   data2={"mobnum": "9876543212",
          "otp": otp}
   response2=test_client.post("/login-verify",json=data2)
#    assert response.status_code==200
#    assert response2.status_code==200
   return response2.json()["access_token"]


   




def test_user_registration (test_client):
   data={
  "name": "string",
  "email": "string",
  "mobnum": "1234567890",
  "gender": "male"
}
   response=test_client.post("/registration",json=data)
   otp=response.json()
   data2={
  "mobnum": "1234567890",
  "otp": otp
}
   response2=test_client.post("/register-verify",json=data2)

   assert response.status_code==200
   assert response2.status_code==200


def test_request(test_user_login,test_client):
   header={"Authorization": f"Bearer {test_user_login}"}
   data={
  "pickup_loc": "string",
  "pickup_loc_long": 0,
  "pickup_loc_lat": 0,
  "drop_loc": "string",
  "drop_loc_long": 0,
  "drop_loc_lat": 0
}
   response=test_client.post("/req-porter",json=data,headers=header)
   print(response.json())
   assert response.status_code==200

def test_accept_user(test_client,test_user_login,db_session):
   header={"Authorization": f"Bearer {test_user_login}"}
   data={
  "pickup_loc": "string",
  "pickup_loc_long": 0,
  "pickup_loc_lat": 0,
  "drop_loc": "string",
  "drop_loc_long": 0,
  "drop_loc_lat": 0
}
   response=test_client.post("/req-porter",json=data,headers=header)
   
   decode=jwt.decode(test_user_login,os.getenv("SECRET_KEY"),algorithms=["HS256"])
   ride= db_session.query(porter).filter(porter.user_id==decode["id"]).one()
   response1=test_client.patch(f"/accept-porter/{ride.id}",headers=header)
   assert response1.status_code== 403
   print(response1.json())
   assert response1.status_code==403
   assert response1.json()["detail"] == "This operation is not allowed by your role."

@patch("routers.porter_req.radius_expansion.apply_async")
def test_accept_driver(mock_async,test_client,test_driver_login,db_session):
   
   header={"Authorization": f"Bearer {test_driver_login}"}
   decode=jwt.decode(test_driver_login,os.getenv("SECRET_KEY"),algorithms=["HS256"])
   driver=db_session.query(Driver).filter(Driver.account_id==decode["id"]).one()
   user1=db_session.query(Accounts).filter(Accounts.mobnum=="9876543210").one()
   db = TestSessionlocal()
   ride1=porter(driver_id=driver.id,user_id=user1.id,status=Status.ACCEPTED,pickup_loc="random",pickup_loc_long=0,pickup_loc_lat=0,drop_loc="random",drop_loc_long=0,drop_loc_lat=0,requested_at=datetime.now(timezone.utc).isoformat(),accepted_at=datetime.now(timezone.utc).isoformat())
   ride2=porter(user_id=user1.id,status=Status.REQUESTED,pickup_loc="random",pickup_loc_long=0,pickup_loc_lat=0,drop_loc="random",drop_loc_long=0,drop_loc_lat=0,requested_at=datetime.now(timezone.utc).isoformat())
   
   db.add(ride1)
   db.add(ride2)
   db.commit()
   ride2_id=ride2.id
   
   db.close()
   r.zadd(f"eligible_drivers:{ride2_id}",{str(decode["id"]):0.0})
   response=test_client.patch(f"/accept-porter/{ride2_id}",headers=header)
   print("i am here")
   r.delete(f"eligible_drivers:{ride2_id}")
   assert response.status_code==403
   assert response.json()["detail"] == "You are not allowed to take up this request."


@patch("routers.porter_req.radius_expansion.apply_async")
def test_accept_driver_happy(mock_async,test_client,test_driver_login,db_session):
   
   header={"Authorization": f"Bearer {test_driver_login}"}
   decode=jwt.decode(test_driver_login,os.getenv("SECRET_KEY"),algorithms=["HS256"])
   driver=db_session.query(Driver).filter(Driver.account_id==decode["id"]).one()
   user1=db_session.query(Accounts).filter(Accounts.mobnum=="9876543210").one()
   db = TestSessionlocal()
   ride=porter(user_id=user1.id,status=Status.REQUESTED,pickup_loc="random",pickup_loc_long=0,pickup_loc_lat=0,drop_loc="random",drop_loc_long=0,drop_loc_lat=0,requested_at=datetime.now(timezone.utc).isoformat())
   db.add(ride)
   db.commit()
   ride_id=ride.id
   
   db.close()
   r.zadd(f"eligible_drivers:{ride_id}",{str(decode["id"]):0.0})
   response=test_client.patch(f"/accept-porter/{ride_id}",headers=header)
   print("i am here")
   r.delete(f"eligible_drivers:{ride_id}")
   assert response.status_code==200
   assert "Accepted wow" in response.json()


   

   
   
   

