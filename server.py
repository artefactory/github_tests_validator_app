from typing import Any

import logging
import traceback

import uvicorn
from fastapi import FastAPI, Request
from github_tests_validator_app.bin.github_event_process import run

app = FastAPI()


@app.post("/")
async def main(request: Request):

    try:
        payload = await request.json()
        run(payload)
    except:
        formatted_exception = traceback.format_exc()
        logging.error(formatted_exception)


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, log_level="info")
