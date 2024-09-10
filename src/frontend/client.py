import asyncio
import websockets


async def receive_messages(websocket):
    async for message in websocket:
        print(f"\n{message}\n> ", end="")


async def send_messages(websocket, username):
    while True:
        message = input("> ")
        if message:
            full_message = f"{username}: {message}"
            await websocket.send(full_message)


async def main():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        print("Connected to the WebSocket server")
        username = input("Enter your username: ")

        # Start background task to listen for incoming messages
        await asyncio.create_task(receive_messages(websocket))

        # Start sending messages
        await send_messages(websocket, username)


if __name__ == "__main__":
    asyncio.run(main())
