import websockets
import asyncio

CHROME_WS_URL = "ws://localhost:8765"  # match with extension server

async def send_command(command):
    try:
        async with websockets.connect(CHROME_WS_URL) as websocket:
            await websocket.send(command)
    except Exception as e:
        print(f"[WebSocket] Error sending command: {e}")
