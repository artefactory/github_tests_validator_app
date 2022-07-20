import uvicorn
from fastapi import FastAPI, Request
from github import GithubIntegration
from github_tests_validator_app.constants import (
    APP_ID,
    APP_KEY,
    SOLUTION_OWNER,
    SOLUTION_REPO_NAME,
    SOLUTION_TESTS_ACCESS_TOKEN,
    TESTS_FOLDER_NAME,
)
from github_tests_validator_app.utils import compare_tests_folder, get_repo

app = FastAPI()

git_integration = GithubIntegration(
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
    token = git_integration.get_access_token(
        git_integration.get_installation(owner, repo_name).id
    ).token

    student_repo = get_repo(token, owner, repo_name)
    solution_repo = get_repo(SOLUTION_TESTS_ACCESS_TOKEN, SOLUTION_OWNER, SOLUTION_REPO_NAME)

    tests_havent_changed = compare_tests_folder(student_repo, solution_repo)
    print(tests_havent_changed)

    return


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, log_level="info")
