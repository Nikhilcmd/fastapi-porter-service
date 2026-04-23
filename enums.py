from enum import Enum

class Gender(Enum):
    MALE= "male"
    FEMALE= "female"

class Role(Enum):
    USER= "user"
    ADMIN= "admin"
    DRIVER="driver"

class Verification(Enum):
    PENDING="pending"
    APPROVED="approved"
    REJECTED="rejected"

class Vechile_type(Enum):
    ELECTRIC="electric"
    NORMAL="normal"

class Status(Enum):
    REQUESTED="requested"
    ACCEPTED="accepted"
    COLLECTED="collected"
    STARTED="started"
    REACHED="reached"
    DROPPED="dropped"
    CANCELLED="cancelled"
    USER_CANCELLED="user_cancelled"


