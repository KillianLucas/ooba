import asyncio
import websockets

"""Not needed anymore?"""

async def check_websocket(port, uri='ws://localhost'):
    uri = f"{uri}:{port}"
    try:
        async with websockets.connect(uri, close_timeout=1):
            return port
    except Exception as e:
        #print(f"Failed to connect to {uri}: {str(e)}")
        return None

async def get_open_ports(start_port=2000, end_port=10000, host='localhost', timeout=1.0):
    tasks = [
        check_websocket(port, f"ws://{host}") for port in range(start_port, end_port + 1)
    ]
    open_ports = await asyncio.gather(*tasks)
    return [port for port in open_ports if port is not None]

# Example usage
async def main():
    open_ports = await get_open_ports(2000, 2020)
    print(f"Open WebSocket ports: {open_ports}")

# To run the example
if __name__ == "__main__":
    asyncio.run(main())