from pydantic import BaseModel
from enums import Gender,Role,Verification, Status
import datetime



class AccountModel(BaseModel):
    name: str
    email: str
    mobnum: str
    gender: Gender

class DriverModel(BaseModel):
    govt_id:str
    Vechile_Number: str
    Vechile_type: str

class porterModel(BaseModel):
    pickup_loc:str
    drop_loc: str

class otp_reg(BaseModel):
    mobnum: str
    otp: str

class otp_login(BaseModel):
    mobnum: str


    
    

