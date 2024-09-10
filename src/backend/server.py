import asyncio
from typing import Set

import websockets
from websockets import WebSocketServerProtocol

connected_clients: Set[WebSocketServerProtocol] = set()


async def handle_client(websocket: WebSocketServerProtocol):
    # Register the new client
    connected_clients.add(websocket)
    try:
        # Receive the username as the first message
        username = await websocket.recv()

        # Notify all clients about the new user
        new_user_message = f"NEW_USER:{username}"
        await asyncio.gather(*[client.send(new_user_message) for client in connected_clients])

        async for message in websocket:
            # Broadcast the message to all connected clients
            await asyncio.gather(*[client.send(message) for client in connected_clients])
    finally:
        # Unregister the client
        connected_clients.remove(websocket)


async def main():
    server = await websockets.serve(handle_client, "localhost", 6789)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())