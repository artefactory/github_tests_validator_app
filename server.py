import uvicorn
from fastapi import FastAPI, Request

from github_management.github_validator_app import github_validator_repo


app = FastAPI()

@app.post("/")
async def main(request: Request) -> None:
    payload = await request.json()

    tests_havent_changed = github_validator_repo(payload)
    return tests_havent_changed


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, log_level="info")
