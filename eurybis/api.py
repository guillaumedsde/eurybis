import asyncio
import http
import pathlib

import fastapi

app = fastapi.FastAPI()

CHUNK_SIZE = 20_000_000  # 20MB

SOCKET_PATH = pathlib.Path("/tmp/lidir.sock")


@app.post("/transferables/")
async def create_transferable(request: fastapi.Request):
    reader, writer = await asyncio.open_unix_connection(SOCKET_PATH)
    bytes_sent = 0
    # Chunks are dependent on the ASGI implementation, see:
    # https://github.com/Kludex/starlette/issues/2590
    async for chunk in request.stream():
        writer.write(chunk)
        bytes_sent += len(chunk)
        if bytes_sent % CHUNK_SIZE == 0:
            await writer.drain()
    writer.close()
    await writer.wait_closed()

    return fastapi.Response(status_code=http.HTTPStatus.OK)
