from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, WebSocketException
import jwt
import os
from database import r

from auth import get_current_user




driver_loc= APIRouter()

@driver_loc.websocket("/driver_loc")
async def driver_location(websocket: WebSocket, token: str):
    
    await websocket.accept()
    
    try:
        while True:
            try:
                decode=jwt.decode(token,os.getenv("SECRET_KEY"),algorithms=["HS256"])
            except jwt.exceptions.ExpiredSignatureError:
                raise WebSocketException(code=1008,reason="The token expired")
            except jwt.exceptions.ImmatureSignatureError:
                raise WebSocketException(code=1008,reason="Invalid token signature.")
            driver_acc_id=decode["id"]
            data=await websocket.receive_json()
            coords = (data["long"], data["lat"],driver_acc_id)
            r.geoadd("driver_location",coords)
            r.set(f"driver_online:{driver_acc_id}",driver_acc_id,ex=30)
    except WebSocketDisconnect:
        pass


