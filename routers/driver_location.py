from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, WebSocketException
import jwt
import os
from database import r,ar
import asyncio
from auth import get_current_user
from datetime import datetime, UTC, timedelta




driver_loc= APIRouter()

@driver_loc.websocket("/driver_loc")
async def driver_location(websocket: WebSocket, token: str):
    
    await websocket.accept()
    try:
        decode=jwt.decode(token,os.getenv("SECRET_KEY"),algorithms=["HS256"])
        driver_acc_id=decode["id"]
        expire_time=decode["exp"]
    except jwt.exceptions.ExpiredSignatureError:
        raise WebSocketException(code=1008,reason="The token expired")
    except jwt.exceptions.ImmatureSignatureError:
        raise WebSocketException(code=1008,reason="Invalid token signature.")

    thechannel=ar.pubsub()
    sub= await thechannel.subscribe(f"driver:{driver_acc_id}")
    


    async def receive_data():
        while True:
            if datetime.now(tz=UTC) < datetime.fromtimestamp(expire_time,tz=UTC):           
                data=await websocket.receive_json()
                coords = (data["long"], data["lat"],driver_acc_id)
                r.geoadd("driver_location",coords)
                r.set(f"driver_online:{driver_acc_id}",driver_acc_id,ex=30)
            else:
                 raise WebSocketException(code=1008,reason="The token expired fake")
                 
    
    async def push_notification():
        async for n in thechannel.listen():
            if n["type"] == "message":
                await websocket.send_json(n["data"])   
    
        


    
    try:
        await asyncio.gather(receive_data(), push_notification())
                

    except WebSocketDisconnect:
        pass


