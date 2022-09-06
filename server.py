from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from github_tests_validator_app.bin.github_event_process import validator

app = FastAPI()


@app.post("/")
async def main(request: Request) -> Any:
    payload = await request.json()

    tests_havent_changed = validator(payload)
    return tests_havent_changed


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, log_level="info")
