from typing import Any

import uvicorn
from bin.validator import validator
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/")
async def main(request: Request) -> Any:
    payload = await request.json()

    tests_havent_changed = validator(payload)
    return tests_havent_changed


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, log_level="info")
