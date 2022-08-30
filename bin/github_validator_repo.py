from typing import Any, Dict, Optional, Union

import logging

from config.config import TESTS_FOLDER_NAME, commit_sha_path
from github import ContentFile
from lib.connectors.github_connector import GitHubConnector
from lib.user import GitHubUser


def get_trigger(payload: Dict[str, Any]) -> Any:
    for trigger in commit_sha_path:
        if trigger in payload:
            return trigger
    return None


def get_student_branch(payload: Dict[str, Any], trigger: Union[str, None] = None) -> Any:
    trigger = get_trigger(payload) if not trigger else trigger
    if not trigger:
        # Log error
        # FIXME
        # Archive the payload
        # FIXME
        logging.error("Couldn't find the student branch, maybe the trigger is not managed")
        return None

    path = commit_sha_path[trigger].copy()
    branch = payload
    while path:

        try:
            branch = branch[path.pop(0)]
        except KeyError as key_err:
            logging.error(key_err)
            return None
        except Exception as err:
            logging.error(err)
            return None

    return branch


def get_student_github_connector(
    student: GitHubUser, payload: Dict[str, Any]
) -> Union[GitHubConnector, None]:

    if student is None:
        return None

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
