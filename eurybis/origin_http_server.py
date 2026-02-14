import asyncio

from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

config = Config()
config.bind = ["localhost:8080"]  # As an example configuration setting
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    asyncio.run(serve(app, config))  # type: ignore
