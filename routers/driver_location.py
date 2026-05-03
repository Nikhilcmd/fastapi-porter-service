from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import jwt
import os
from database import r

from auth import get_current_user




driver_loc= APIRouter()

@driver_loc.websocket("/driver_loc")
async def driver_location(websocket: WebSocket, token: str):
    try:
     decode=jwt.decode(token,os.getenv("SECRET_KEY"),algorithms=["HS256"])
    except jwt.exceptions.ExpiredSignatureError:
       raise HTTPException(status_code=401,detail="Token Expired")
    except jwt.exceptions.ImmatureSignatureError:
       raise HTTPException(status_code=401,detail="Invalid token")
    await websocket.accept()
    driver_acc_id=decode["id"]
    try:
        while True:
            
            data=await websocket.receive_json()
            coords = (data["long"], data["lat"],driver_acc_id)
            r.geoadd("driver_location",coords)
            r.set(f"driver_online:{driver_acc_id}",driver_acc_id,ex=30)
    except WebSocketDisconnect:
        pass


