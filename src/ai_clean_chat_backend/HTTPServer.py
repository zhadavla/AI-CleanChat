# src/ai_clean_chat_backend/HTTPServer.py
import json
import os
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from ai_clean_chat_backend import predict_harmful
from ai_clean_chat_backend.database import get_db, User, Message

app: FastAPI = FastAPI()

connected_clients: Dict[WebSocket, str] = {}

import logging

logging.basicConfig(level=logging.INFO)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    username = await websocket.receive_text()

    logging.info(f"User {username} has joined.")

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

    # Send chat   to the new user
    messages = db.query(Message).all()
    history = [{"user": message.user.name, "content": message.content, "timestamp": message.timestamp}
               for message in messages]
    logging.info(f"Sending chat history to {username}: {history}")
    await websocket.send_text(f"HISTORY:{json.dumps(history)}")

    # Send the list of online users to the new user
    online_users = [client_name for client_name in connected_clients.values()]
    logging.info(f"Online users: {online_users}")
    await websocket.send_text(f"ONLINE_USERS:{json.dumps(online_users)}")

    # Notify all clients that a new user has joined
    await broadcast(f"{username} has joined the chat!")
    await broadcast_online_users()

    try:
        while True:
            message_text = await websocket.receive_text()

            # Save message in the database
            new_message = Message(content=message_text, user_id=user.id, timestamp=str(datetime.now()))

            def predict_harmfulness(text: str) -> bool:
                import random
                return random.choice([True, False])

            # Check if the message is harmful and broadcast it accordingly
            if predict_harmfulness(message_text):
                new_message.is_harmful = True
                message_to_broadcast = f"HARMFUL:{username}:{message_text}"
                logging.info(f"Broadcasting {{{message_to_broadcast}}} ")
                await broadcast(f"HARMFUL_MESSAGE:{username}:{message_text}")
            else:
                logging.info(f"Broadcasting {{{message_text}}} ")
                await broadcast(f"MESSAGE:{username}: {message_text}")


            db.add(new_message)
            db.commit()
    except WebSocketDisconnect:
        # Mark user as offline in DB
        user.is_online = False
        db.commit()

        # Remove from connected clients
        del connected_clients[websocket]
        await broadcast(f"{username} has left the chat.")
        await broadcast_online_users()


async def broadcast(message: str):
    for client in connected_clients:
        await client.send_text(message)


async def broadcast_online_users():
    # Broadcast the updated list of online users to all clients
    online_users = [client_name for client_name in connected_clients.values()]
    for client in connected_clients:
        await client.send_text(f"ONLINE_USERS:{json.dumps(online_users)}")


# Define the base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/")
async def get():
    # refresh static everytime server restarted
    version = "v1.0"
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    with open(index_path, 'r') as f:
        html_content = f.read().replace("/static/chat.js", f"/static/chat.js?version={version}")
        return HTMLResponse(html_content)
