import uvicorn
from fastapi import FastAPI, Request
from github import Github, GithubIntegration
from github_tests_validator_app.constants import APP_ID, APP_KEY
from github_tests_validator_app.utils import get_hash_files

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

    git_connection = Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(owner, repo_name).id
        ).token
    )

    repo = git_connection.get_repo(f"{owner}/{repo_name}")
    contents = repo.get_contents("tests")
    hashes = get_hash_files(contents)
    print(hashes)
    return


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, log_level="info")
