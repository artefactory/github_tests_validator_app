from typing import Any, Dict

import logging

from bin.github_validator_repo import (
    get_student_github_connector,
    get_trigger,
    github_validator_repo,
)
from config.config import (
    SOLUTION_OWNER,
    SOLUTION_REPO_NAME,
    SOLUTION_TESTS_ACCESS_TOKEN,
    default_message,
)
from lib.connectors.github_connector import GitHubConnector
from lib.connectors.google_sheet_connector import GSheet
from lib.user import GitHubUser
from lib.utils import get_github_user


def validator(payload: Dict[str, Any]) -> Any:
    # Init trigger
    trigger = get_trigger(payload)
    if not trigger or (
        trigger == "pull_request" and payload["action"] not in ["reopened", "opened"]
    ):
        return

    # Init Google Sheet
    gsheet = GSheet()

    # Init GitHubUser
    student_user = get_github_user(payload)
    solution_user = GitHubUser(LOGIN=str(SOLUTION_OWNER), ACCESS_TOKEN=SOLUTION_TESTS_ACCESS_TOKEN)

    # Add user on Google Sheet
    gsheet.add_new_user_on_sheet(student_user)

    # Check valid repo
    student_github_connector = get_student_github_connector(student_user, payload)
    if not student_github_connector:
        gsheet.add_new_repo_valid_result(
            student_user,
            "Connect to student repository",
            False,
            "[ERROR]: cannot get the student github repository.",
        )
        logging.error("[ERROR]: cannot get the student github repository.")
        return

    solution_github_connector = GitHubConnector(solution_user, SOLUTION_REPO_NAME, "main")
    if not student_github_connector:
        gsheet.add_new_repo_valid_result(
            student_user,
            "Connect to school_of_data_tests repository",
            False,
            "[ERROR]: cannot get the solution github repository.",
        )
        logging.error("[ERROR]: cannot get the solution github repository.")
        return

    tests_havent_changed = github_validator_repo(
        student_github_connector, solution_github_connector
    )

    # Add valid repo result on Google Sheet
    gsheet.add_new_repo_valid_result(
        student_user,
        "Check the test folder",
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
