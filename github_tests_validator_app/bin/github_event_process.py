from typing import Any, Dict, List

import logging

from github_tests_validator_app.bin.github_repo_validation import (
    get_event,
    get_student_github_connector,
    github_repo_validation,
)
from github_tests_validator_app.bin.student_challenge_results_validation import (
    send_student_challenge_results,
)
from github_tests_validator_app.config.config import (
    GDRIVE_MAIN_DIRECTORY_NAME,
    GDRIVE_SUMMARY_SPREADSHEET,
    GSHEET_DETAILS_SPREADSHEET,
    USER_SHARE,
)
from github_tests_validator_app.lib.connectors.gddrive import GoogleDriveConnector
from github_tests_validator_app.lib.connectors.gsheet import GSheetConnector
from github_tests_validator_app.lib.models.file import GSheetDetailFile, GSheetFile, WorkSheetFile
from github_tests_validator_app.lib.models.users import GitHubUser
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
        or (
            event == "workflow_job"
            and (
                payload["action"] not in ["completed"]
                or payload["workflow_job"]["conclusion"] != "success"
            )
        )
    ):
        return ""
    return event


def init_gsheet_file(
    google_drive: GoogleDriveConnector,
    info: Dict[str, Any],
    parent_id: str,
    shared_user_list: List[str],
) -> GSheetFile:

    gsheet = google_drive.get_gsheet(info["name"], parent_id, shared_user_list)
    list_worksheets = [
        WorkSheetFile(NAME=worksheet["name"], HEADERS=worksheet["headers"])
        for _, worksheet in info["worksheets"].items()
    ]
    return GSheetFile(
        NAME=info["name"],
        MIMETYPE=gsheet.get("mimeType", ""),
        ID=gsheet.get("id", ""),
        WORKSHEETS=list_worksheets,
    )


def init_gsheet_detail_file(
    google_drive: GoogleDriveConnector, info: Dict[str, Any], parent_id: str, user_share: List[str]
) -> GSheetDetailFile:

    gsheet = google_drive.get_gsheet(info["name"], parent_id, user_share)
    return GSheetDetailFile(
        NAME=info["name"],
        MIMETYPE=gsheet.get("mimeType", ""),
        ID=gsheet.get("id", ""),
        HEADERS=info["headers"],
    )


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

    # Init Google Drive connector and folders
    google_drive = GoogleDriveConnector()
    folder_school_of_data = google_drive.get_gdrive_folder(GDRIVE_MAIN_DIRECTORY_NAME, USER_SHARE)

    # Init Google sheets
    gsheet_summary_file = init_gsheet_file(
        google_drive, GDRIVE_SUMMARY_SPREADSHEET, folder_school_of_data["id"], USER_SHARE
    )
    gsheet_details_file = init_gsheet_detail_file(
        google_drive, GSHEET_DETAILS_SPREADSHEET, folder_school_of_data["id"], USER_SHARE
    )

    # Init Google sheet connector and worksheets
    gsheet = GSheetConnector(google_drive.credentials, gsheet_summary_file, gsheet_details_file)

    # Init GitHubUser
    student_user = init_github_user_from_github_event(payload)
    if not isinstance(student_user, GitHubUser):
        # Logging
        return

    # Send user on Google Sheet
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

    logging.info(f'Begin process: "{event}"...')
    # Run the process
    process[event](student_github_connector, gsheet, payload)
    logging.info(f'End of process: "{event}".')
