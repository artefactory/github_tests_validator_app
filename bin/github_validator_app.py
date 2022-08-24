from typing import Any, Dict, Tuple

from config import (
    APP_ID,
    APP_KEY,
    SOLUTION_OWNER,
    SOLUTION_REPO_NAME,
    SOLUTION_TESTS_ACCESS_TOKEN,
    TESTS_FOLDER_NAME,
)
from github import ContentFile, GithubIntegration
from lib.connectors.github_connector import GithubConnector

git_integration = GithubIntegration(
    APP_ID,
    APP_KEY,
)

triggers = {"pull_request": ["pull_request", "head", "ref"], "pusher": ["ref"]}


def get_student_branch(payload: Dict[str, Any]) -> Any:
    for trigger in triggers:
        if trigger in payload:
            branch = payload
            path = triggers[trigger]
            while path:
                branch = branch[path.pop(0)]
            return branch
    return None


def get_student_creds(payload: Dict[str, Any]) -> Tuple[str, str, str]:

    owner = payload["repository"]["owner"]["login"]
    repo_name = payload["repository"]["name"]
    token = git_integration.get_access_token(
        git_integration.get_installation(owner, repo_name).id
    ).token
    return owner, repo_name, token


def compare_tests_folder(
    student_repo: GithubConnector, solution_repo: GithubConnector, student_branch_repo: str
) -> Any:

    student_contents = student_repo.repo.get_contents(TESTS_FOLDER_NAME, ref=student_branch_repo)

    if (
        isinstance(student_contents, ContentFile.ContentFile)
        and student_contents.type == "submodule"
    ):
        solution_last_commit = solution_repo.get_last_hash_commit("main")
        student_tests_commit = student_contents.sha
        return solution_last_commit == student_tests_commit

    student_hash_tests = student_repo.get_tests_hash(TESTS_FOLDER_NAME)
    solution_hash_tests = solution_repo.get_tests_hash(TESTS_FOLDER_NAME)
    return student_hash_tests == solution_hash_tests


def github_validator_repo(payload: Dict[str, Any]) -> Any:

    student_owner, student_repo_name, student_token = get_student_creds(payload)
    student_github = GithubConnector(student_token, student_owner, student_repo_name)
    student_branch = get_student_branch(payload)
    if student_branch is None:
        # Log error
        # FIXME
        # Archive the payload
        # FIXME
        # print("Could'nt find the student commit, maybe the trigger is not managed")
        return False
    solution_github = GithubConnector(
        SOLUTION_TESTS_ACCESS_TOKEN, SOLUTION_OWNER, SOLUTION_REPO_NAME
    )

    # Valide of repo
    tests_havent_changed = compare_tests_folder(student_github, solution_github, student_branch)

    # Send results to GCP
    # FIXME

    # Results of challenges
    # FIXME
    return tests_havent_changed
