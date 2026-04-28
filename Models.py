from pydantic import BaseModel
from enums import Gender,Role,Verification, Status, Vechile_type
import datetime



class AccountModel(BaseModel):
    name: str
    email: str
    mobnum: str
    gender: Gender

class DriverModel(BaseModel):
    govt_id:str
    Vechile_Number: str
    Vechile_type: Vechile_type 

class porterModel(BaseModel):
    pickup_loc:str
    pickup_loc_long:float
    pickup_loc_lat:float
    drop_loc: str
    drop_loc_long: float
    drop_loc_lat: float
    


class otp_reg(BaseModel):
    mobnum: str
    otp: str

class otp_login(BaseModel):
    mobnum: str


    
    

