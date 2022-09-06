from typing import Any, Dict, Union

import logging

from github import ContentFile
from github_tests_validator_app.config.config import (
    GH_SOLUTION_OWNER,
    GH_SOLUTION_REPO_NAME,
    GH_SOLUTION_TESTS_ACCESS_TOKEN,
    GH_TESTS_FOLDER_NAME,
    commit_sha_path,
    default_message,
)
from github_tests_validator_app.lib.connectors.github_connector import GitHubConnector
from github_tests_validator_app.lib.connectors.google_sheet_connector import GSheet
from github_tests_validator_app.lib.users import GitHubUser


def get_event(payload: Dict[str, Any]) -> Any:
    for event in commit_sha_path:
        if event in payload:
            return event
    return None


def get_student_branch(payload: Dict[str, Any], trigger: Union[str, None] = None) -> Any:
    trigger = get_event(payload) if not trigger else trigger
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

    if not student:
        return None

    github_student_branch = get_student_branch(payload)
    if github_student_branch is None:
        return None

    repo_name = payload["repository"]["name"]
    student.get_access_token(repo_name)
    return GitHubConnector(student, repo_name, github_student_branch)


def compare_tests_folder(student_github: GitHubConnector, solution_repo: GitHubConnector) -> Any:

    student_contents = student_github.repo.get_contents(
        GH_TESTS_FOLDER_NAME, ref=student_github.BRANCH_NAME
    )

    if (
        isinstance(student_contents, ContentFile.ContentFile)
        and student_contents.type == "submodule"
    ):
        solution_last_commit = solution_repo.get_last_hash_commit()
        student_tests_commit = student_contents.sha
        return solution_last_commit == student_tests_commit

    student_hash_tests = student_github.get_tests_hash(GH_TESTS_FOLDER_NAME)
    solution_hash_tests = solution_repo.get_tests_hash(GH_TESTS_FOLDER_NAME)
    return student_hash_tests == solution_hash_tests


def github_repo_validation(
    student_github_connector: GitHubConnector, gsheet: GSheet, payload: Dict[str, Any]
) -> None:

    solution_user = GitHubUser(
        LOGIN=str(GH_SOLUTION_OWNER), ACCESS_TOKEN=GH_SOLUTION_TESTS_ACCESS_TOKEN
    )
    solution_github_connector = GitHubConnector(solution_user, GH_SOLUTION_REPO_NAME, "main")
    if not solution_github_connector:
        gsheet.add_new_repo_valid_result(
            solution_user,
            False,
            "[ERROR]: cannot get the solution github repository.",
        )
        logging.error("[ERROR]: cannot get the solution github repository.")
        return

    tests_havent_changed = compare_tests_folder(student_github_connector, solution_github_connector)

    # Add valid repo result on Google Sheet
    gsheet.add_new_repo_valid_result(
        student_github_connector.user,
        tests_havent_changed,
        default_message["valid_repository"][str(tests_havent_changed)],
    )

    # Update Pull Request
    if "pull_request" in payload:
        issue = student_github_connector.repo.get_issue(number=payload["pull_request"]["number"])
        message = default_message["valid_repository"][str(tests_havent_changed)]
        issue.create_comment(message)
        conclusion = "success" if tests_havent_changed else "failure"
        student_github_connector.repo.create_check_run(
            name=message,
            head_sha=payload["pull_request"]["head"]["sha"],
            status="completed",
            conclusion=conclusion,
        )
