import asyncio

from websockets import ServerConnection
from websockets.asyncio.server import serve

from skynet_backend.logging_config import root_logger


async def start_llm_conversation(websocket_server_connection: ServerConnection):
    if (
        websocket_server_connection.request is not None
        and websocket_server_connection.request.path != "/api/llm-conversation"
    ):
        return

    await websocket_server_connection.send("Test message")


async def start_websockets_server():
    root_logger.info("Starting websockets server")

    async with serve(start_llm_conversation, host="localhost", port=8000) as server:
        await server.serve_forever()


asyncio.run(start_websockets_server())
