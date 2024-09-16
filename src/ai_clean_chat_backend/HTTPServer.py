# src/ai_clean_chat_backend/HTTPServer.py
import json
import os
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from ai_clean_chat_backend import predict_harmful
from ai_clean_chat_backend.database import get_db, User, Message
from ai_clean_chat_backend.predict_harmful import predict_harmfulness

app: FastAPI = FastAPI()

connected_clients: Dict[WebSocket, str] = {}

import logging

logging.basicConfig(level=logging.INFO)


async def send_history(websocket: WebSocket, db: Session):
    # Fetch and structure the message history
    messages = db.query(Message).all()
    history = [
        {
            "type": "message",
            "subtype": "clean" if not message.is_harmful else "harmful",
            "data": {"user": message.user.name, "content": message.content, "timestamp": message.timestamp}
        }
        for message in messages
    ]
    history_message = {
        "type": "history",
        "data": history
    }
    await websocket.send_text(json.dumps(history_message))


async def broadcast_new_user(username: str):
    # Notify all clients that a new user has joined
    message = {
        "type": "new_user",
        "data": {
            "user": username,
            "content": "has joined the chat!",
            "timestamp": str(datetime.now())
        }
    }
    await broadcast(json.dumps(message))


async def broadcast_message(username: str, message: str):
    message = {
        "type": "message",
        "data": {
            "user": username,
            "content": message,
            "timestamp": str(datetime.now())
        }
    }
    await broadcast(json.dumps(message))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    username = await websocket.receive_text()

    # Mark user as online
    user = db.query(User).filter(User.name == username).first()

    if not user:
        user = User(name=username, is_online=True)
        db.add(user)
    else:
        user.is_online = True
    db.commit()

    # Add user to connected_clients
    connected_clients[websocket] = username

    await send_history(websocket, db)

    # Notify all clients that a new user has joined
    await broadcast_new_user(username)
    await send_online_users(websocket)

    try:
        while True:
            message_text = await websocket.receive_text()

            # Save message in the database
            new_message = Message(content=message_text, user_id=user.id, timestamp=str(datetime.now()))

            to_send: json = {
                "type": "message",
                "subtype": "clean",
                "data": {
                    "user": username,
                    "content": message_text,
                    "timestamp": str(datetime.now())
                },
            }
            # Run harmfulness prediction in a threadpool to avoid blocking the WebSocket event loop
            harmful_prediction = await run_in_threadpool(predict_harmfulness, [message_text])

            # Check the prediction and update the message subtype if it's harmful
            if harmful_prediction[0] == "hate_speech" or harmful_prediction[0] == "offensive_language":
                new_message.is_harmful = True
                to_send["subtype"] = "harmful"

            await broadcast(json.dumps(to_send))

            db.add(new_message)
            db.commit()
    except WebSocketDisconnect:
        # Mark user as offline in DB
        user.is_online = False
        db.commit()

        # Remove from connected clients
        del connected_clients[websocket]
        to_send = {
            "type": "user_left",
            "data": {
                "user": username,
                "content": "has left the chat!",
                "timestamp": str(datetime.now())
            }
        }
        await broadcast(json.dumps(to_send))
        await send_online_users(websocket)


async def broadcast(message: str):
    for client in connected_clients:
        await client.send_text(message)


async def send_online_users(websocket):
    # Structure and send the list of online users
    online_users = [client_name for client_name in connected_clients.values()]
    online_users_message = {
        "type": "online_users",
        "data": online_users
    }
    for client in connected_clients:
        await client.send_text(json.dumps(online_users_message))


# Define the base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f'{BASE_DIR=}')

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/")
async def get():
    # refresh static everytime server restarted
    version = "v1.0"
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    with open(index_path, 'r') as f:
        html_content = f.read() \
            .replace("/static/chat.js", f"/static/chat.js?version={version}") \
            .replace("/static/chat.css", f"/static/chat.css?version={version}")

        return HTMLResponse(html_content)

if __name__ == "__main__":
    # print current dir
    print(os.getcwd())