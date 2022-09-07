from typing import Any, Dict

import logging

from github_tests_validator_app.bin.github_repo_validation import (
    get_event,
    get_student_github_connector,
    github_repo_validation,
)
from github_tests_validator_app.bin.student_challenge_results_validation import (
    send_student_challenge_results,
)
from github_tests_validator_app.lib.connectors.gsheet import GSheetConnector
from github_tests_validator_app.lib.users import GitHubUser
from github_tests_validator_app.lib.utils import init_github_user_from_github_event

process = {
    "pull_request": github_repo_validation,
    "pusher": github_repo_validation,
    "workflow_job": send_student_challenge_results,
}


def handle_process(payload: Dict[str, Any]) -> str:
    # Get event
    event = get_event(payload)
    if (
        not event
        or (event == "pull_request" and payload["action"] not in ["reopened", "opened"])
        or (event == "workflow_job" and payload["action"] not in ["completed"])
    ):
        return ""
    return event


def run(payload: Dict[str, Any]) -> Any:
    """
    Validator function

    Args:
        payload Dict[str, Any]: information of new event

    Returns:
        None: Return nothing
    """

    event = handle_process(payload)
    if not event:
        return

    # Init Google Sheet
    gsheet = GSheetConnector()

    # Init GitHubUser
    student_user = init_github_user_from_github_event(payload)
    if not isinstance(student_user, GitHubUser):
        # Logging
        return

    # Add user on Google Sheet
    gsheet.add_new_user_on_sheet(student_user)

    # Check valid repo
    student_github_connector = get_student_github_connector(student_user, payload)
    if not student_github_connector:
        gsheet.add_new_repo_valid_result(
            student_user,
            False,
            "[ERROR]: cannot get the student github repository.",
        )
        logging.error("[ERROR]: cannot get the student github repository.")
        return

    logging.info(f"Begin {event} process...")
    # Run the process
    process[event](student_github_connector, gsheet, payload)
    logging.info(f"END of {event} process.")
