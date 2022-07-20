import uvicorn
from fastapi import FastAPI, Request
from github import GithubIntegration
from github_tests_validator_app.constants import (
    APP_ID,
    APP_KEY,
    SOLUTION_OWNER,
    SOLUTION_REPO_NAME,
    SOLUTION_TESTS_ACCESS_TOKEN,
)
from github_tests_validator_app.utils import get_tests_hash

app = FastAPI()

git_intergration = GithubIntegration(
    APP_ID,
    APP_KEY,
)


@app.post("/")
async def main(request: Request) -> None:
    payload = await request.json()

    if payload["action"] not in ["opened", "synchronize"]:
        return

    owner = payload["repository"]["owner"]["login"]
    repo_name = payload["repository"]["name"]
    token = git_intergration.get_access_token(
        git_intergration.get_installation(owner, repo_name).id
    ).token

    student_hash_tests = get_tests_hash(token, owner, repo_name)

    solution_hash_tests = get_tests_hash(
        SOLUTION_TESTS_ACCESS_TOKEN, SOLUTION_OWNER, SOLUTION_REPO_NAME
    )

    print(student_hash_tests)
    print(solution_hash_tests)

    return


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, log_level="info")
