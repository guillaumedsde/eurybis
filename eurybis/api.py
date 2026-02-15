import asyncio
import http
import os

import fastapi

app = fastapi.FastAPI()

CHUNK_SIZE = 1_000_000  # 1MB


@app.post("/transferables/")
async def create_transferable(request: fastapi.Request):
    _, writer = await asyncio.open_unix_connection(os.environ["LIDIS_SOCKET_PATH"])
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
