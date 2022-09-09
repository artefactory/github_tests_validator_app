from typing import Dict, cast

import os

# GitHub
GH_APP_ID = cast(str, os.getenv("GH_APP_ID", None))
GH_APP_KEY_PATH = os.getenv("GH_APP_KEY", "")
GH_SOLUTION_TESTS_ACCESS_TOKEN = cast(str, os.getenv("SOLUTION_TESTS_ACCESS_TOKEN", None))
GH_SOLUTION_OWNER = "artefactory-fr"
GH_SOLUTION_REPO_NAME = "school_of_data_tests"
GH_TESTS_FOLDER_NAME = "tests"
GH_API = "https://api.github.com/repos"
GH_ALL_ARTIFACT_ENDPOINT = "actions/artifacts"

# Google Drive
GDRIVE_CREDENTIALS_PATH = "credentials.json"
GDRIVE_MAIN_DIRECTORY_NAME = "school_of_data_results"

# Google Sheet
GSHEET_SA_JSON = cast(str, os.getenv("GSHEET_SA_JSON", None))
GSHEET_WORKSHEET_STUDENT = "students"
GSHEET_WORKSHEET_CHECK_VALIDATION_REPO = "check_validation_repo"
GSHEET_WORKSHEET_STUDENT_CHALLENGE_RESULT = "student_challenge_results"
GDRIVE_SUMMARY_SPREADSHEET = {
    "NAME": "Student challenge results",
    "WORKSHEETS": [
        {"NAME": GSHEET_WORKSHEET_STUDENT, "HEADERS": ["login", "url", "id", "created_at"]},
        {
            "NAME": GSHEET_WORKSHEET_CHECK_VALIDATION_REPO,
            "HEADERS": ["login", "user_id", "is_valid", "created_at", "info"],
        },
        {
            "NAME": GSHEET_WORKSHEET_STUDENT_CHALLENGE_RESULT,
            "HEADERS": [
                "login",
                "workflow_run_id",
                "created_at",
                "total_tests_collected",
                "total_passed_test",
                "total_failed_test",
                "duration",
                "info",
            ],
        },
    ],
}
GSHEET_DETAILS_SPREADSHEET = {
    "NAME": "Details",
    "HEADERS": [
        "login",
        "workflow_run_id",
        "created_at",
        "file_path",
        "script_name",
        "test_name",
        "outcome",
        "challenge_id",
        "setup",
        "call",
        "teardown",
    ],
}

# Log message
default_message: Dict[str, Dict[str, str]] = {
    "valid_repository": {
        "True": "Your folder `Test` is valid",
        "False": "Your folder `Test` has been modified and is no longer valid.",
    },
}

# Common
CHALLENGE_DIR = "tests/tests/"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
USER_SHARE = os.getenv("USER_SHARE", "")
