import websockets
import asyncio
import threading


WS_URL = "ws://localhost:8000/ws/caseflow/"

async def listen_ws():
    async with websockets.connect(WS_URL) as ws:
        print(f"Connected to WebSocket {WS_URL}")
        while True:
            msg = await ws.recv()
            print("Update:", msg)

def start_ws_listener():
    asyncio.run(listen_ws())

if __name__ == "__main__":
    threading.Thread(target=start_ws_listener, daemon=True).start()

    while True:
        input("Press enter to disconnect\n")
        break