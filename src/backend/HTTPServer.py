from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import the database utilities
from database import get_db, User
from sqlalchemy.exc import IntegrityError

app = FastAPI()

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the frontend folder to serve static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

connected_clients: Set[WebSocket] = set()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        # Receive username from the client
        username = await websocket.receive_text()

        # Add the new user to the database
        try:
            new_user = User(name=username)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()  # In case the user already exists (duplicate username)
            await websocket.send_text(f"ERROR: Username {username} already exists.")
            connected_clients.remove(websocket)
            return

        # Notify all clients about the new user
        new_user_message = f"NEW_USER:{username}"
        await broadcast_message(new_user_message)

        # Keep listening to the WebSocket for new messages
        while True:
            message = await websocket.receive_text()
            await broadcast_message(message)

    except WebSocketDisconnect:
        # Handle disconnection and remove the user from the database
        connected_clients.remove(websocket)
        user = db.query(User).filter(User.name == username).first()
        if user:
            db.delete(user)
            db.commit()
        print(f"Client {username} disconnected")


async def broadcast_message(message: str):
    disconnected_clients = set()

    for client in connected_clients:
        try:
            await client.send_text(message)
        except WebSocketDisconnect:
            disconnected_clients.add(client)

    # Remove disconnected clients
    connected_clients.difference_update(disconnected_clients)


# Serve the HTML file
@app.get("/")
async def get():
    return HTMLResponse(open("../frontend/index.html").read())


# Run the server using Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
