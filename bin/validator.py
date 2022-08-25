from typing import Any, Dict

from bin.github_validator_repo import github_validator_repo
from config import SOLUTION_OWNER, SOLUTION_REPO_NAME, SOLUTION_TESTS_ACCESS_TOKEN
from lib.connectors.github_connector import GitHubConnector
from lib.user import GitHubUser
from lib.utils import get_github_user

triggers = {"pull_request": ["pull_request", "head", "ref"], "pusher": ["ref"]}


def get_trigger(payload: Dict[str, Any]) -> Any:
    for trigger in triggers:
        if trigger in payload:
            return trigger
    return None


def get_student_branch(payload: Dict[str, Any]) -> Any:
    trigger = get_trigger(payload)
    path = triggers[trigger]
    branch = payload
    while path:
        branch = branch[path.pop(0)]
    return branch


def validator(payload: Dict[str, Any]) -> Any:

    # Init Data
    student = get_github_user(payload)
    github_student_branch = get_student_branch(payload)
    if github_student_branch is None:
        # Log error
        # FIXME
        # Archive the payload
        # FIXME
        # print("Could'nt find the student commit, maybe the trigger is not managed")
        return False

    repo_name = payload["repository"]["name"]
    student.get_access_token(repo_name)
    student_github = GitHubConnector(student, repo_name, github_student_branch)

    solution_user = GitHubUser(LOGIN=SOLUTION_OWNER, ACCESS_TOKEN=SOLUTION_TESTS_ACCESS_TOKEN)
    solution_github = GitHubConnector(solution_user, SOLUTION_REPO_NAME, "main")
    tests_havent_changed = github_validator_repo(student_github, solution_github)
    return tests_havent_changed
