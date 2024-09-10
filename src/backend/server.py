#!/usr/bin/env python

import asyncio

from websockets.asyncio.server import serve, ServerConnection


async def hello(websocket: ServerConnection) -> None:
    name = await websocket.recv()
    print(f"<<< {name.__str__()}")

    greeting = f"Hello {name.__str__()}!"

    await websocket.send(greeting)
    print(f">>> {greeting}")


async def main():
    async with serve(hello, "localhost", 8765):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
