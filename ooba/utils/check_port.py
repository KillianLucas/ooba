import websockets

async def check_port(port, uri='ws://localhost', verbose=False):
    uri = f"{uri}:{port}"
    try:
        async with websockets.connect(uri, close_timeout=1):
            return port
    except Exception as e:
        if verbose:
            print(f"Failed to connect to {uri}: {str(e)}")
        return None