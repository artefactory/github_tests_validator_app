from typing import Any, Dict, List

import logging

from github_tests_validator_app.bin.github_repo_validation import (
    get_event,
    get_user_github_connector,
    validate_github_repo,
)
from github_tests_validator_app.bin.user_pytest_summaries_validation import (
    send_user_pytest_summaries,
)
from github_tests_validator_app.lib.connectors.sqlalchemy_client import SQLAlchemyConnector, User
from github_tests_validator_app.lib.utils import init_github_user_from_github_event

process = {
    "pull_request": validate_github_repo,
    "pusher": validate_github_repo,
    "workflow_job": send_user_pytest_summaries,
}


def handle_process(payload: Dict[str, Any]) -> str:
    # Get event
    event: str = get_event(payload)
    if (
        not event
        or (event == "pull_request" and payload["action"] not in ["reopened", "opened"])
        or (event == "workflow_job" and payload["action"] not in ["completed"])
    ):
        return ""
    return event


def run(payload: Dict[str, Any]) -> None:
    """
    Validator function

    Args:
        payload (Dict[str, Any]): information of new event

    Returns:
        None: Return nothing
    """

    event = handle_process(payload)
    if not event:
        return

    # Init User
    user_data = init_github_user_from_github_event(payload)
    if not isinstance(user_data, dict):
        # Logging
        return

    sql_client = SQLAlchemyConnector()
    try:
        sql_client.add_new_user(user_data)
    except Exception as e:
        logging.error(f"[ERROR]: {e}")

    # Check valid repo
    user_github_connector = get_user_github_connector(user_data, payload)
    if not user_github_connector:
        sql_client.add_new_repository_validation(
            user_data,
            False,
            payload,
            event,
            "[ERROR]: cannot get the user github repository.",
        )
        logging.error("[ERROR]: cannot get the user github repository.")
        return

    logging.info(f'Begin process: "{event}"...')
    # Run the process
    process[event](user_github_connector, sql_client, payload, event)
    logging.info(f'End of process: "{event}".')
