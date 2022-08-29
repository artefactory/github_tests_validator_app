from typing import Any, Dict, Union

from config import TESTS_FOLDER_NAME
from github import ContentFile
from lib.connectors.github_connector import GitHubConnector
from lib.user import GitHubUser

triggers = {"pull_request": ["pull_request", "head", "ref"], "pusher": ["ref"]}


def get_trigger(payload: Dict[str, Any]) -> Any:
    for trigger in triggers:
        if trigger in payload:
            return trigger
    return None


def get_student_branch(payload: Dict[str, Any], trigger: Union[str, None] = None) -> Any:
    trigger = get_trigger(payload) if not trigger else None
    if not trigger:
        # Log error
        # FIXME
        # Archive the payload
        # FIXME
        print("Couldn't find the student branch, maybe the trigger is not managed")
        return None
    path = triggers[trigger]
    branch = payload
    while path:
        branch = branch[path.pop(0)]
    return branch


def get_student_github_connector(
    student: GitHubUser, payload: Dict[str, Any]
) -> Union[bool, GitHubConnector]:
    github_student_branch = get_student_branch(payload)
    if github_student_branch is None:
        return None

    repo_name = payload["repository"]["name"]
    student.get_access_token(repo_name)
    return GitHubConnector(student, repo_name, github_student_branch)


def compare_tests_folder(student_github: GitHubConnector, solution_repo: GitHubConnector) -> Any:

    student_contents = student_github.repo.get_contents(
        TESTS_FOLDER_NAME, ref=student_github.BRANCH_NAME
    )

    if (
        isinstance(student_contents, ContentFile.ContentFile)
        and student_contents.type == "submodule"
    ):
        solution_last_commit = solution_repo.get_last_hash_commit()
        student_tests_commit = student_contents.sha
        return solution_last_commit == student_tests_commit

    student_hash_tests = student_github.get_tests_hash(TESTS_FOLDER_NAME)
    solution_hash_tests = solution_repo.get_tests_hash(TESTS_FOLDER_NAME)
    return student_hash_tests == solution_hash_tests


def github_validator_repo(student_github: GitHubConnector, solution_github: GitHubConnector) -> Any:
    # Valide of repo
    tests_havent_changed = compare_tests_folder(student_github, solution_github)

    return tests_havent_changed
