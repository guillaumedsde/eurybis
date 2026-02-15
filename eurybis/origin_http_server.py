import asyncio
import http

import fastapi

app = fastapi.FastAPI()

CHUNK_SIZE = 20_000_000  # 20MB


@app.post("/transferables/")
async def create_transferable(request: fastapi.Request):
    reader, writer = await asyncio.open_connection("127.0.0.1", 6000)

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
