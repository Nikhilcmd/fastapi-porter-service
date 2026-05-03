from fastapi import FastAPI
from routers.user_registration import registration_router
from routers.login import login_router
from routers.driver_reg import driver_router
from routers.admin_ver import admin_router
from routers.porter_req import porter_req
from routers.accept import porter_accept
from routers.driver_location import driver_loc

app=FastAPI()
app.include_router(registration_router)

app.include_router(login_router)

app.include_router(driver_router)

app.include_router(admin_router)

app.include_router(porter_req)

app.include_router(porter_accept)

app.include_router(driver_loc)



