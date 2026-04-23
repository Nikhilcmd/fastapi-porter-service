from fastapi import FastAPI
from routers.user_registration import registration_router
from routers.login import login_router

app=FastAPI()
app.include_router(registration_router)

app.include_router(login_router)

