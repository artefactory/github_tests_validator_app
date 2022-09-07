from typing import Dict, List, cast

import os

from github import GithubIntegration

### GitHub ###
GH_APP_ID = cast(str, os.getenv("GH_APP_ID"))
# APP_KEY = cast(str, os.getenv("GH_APP_KEY"))
GH_APP_KEY_PATH = os.getenv("GH_APP_KEY")
GH_APP_KEY = ""
if GH_APP_KEY_PATH:
    with open(GH_APP_KEY_PATH) as f:
        GH_APP_KEY = f.read()
GH_SOLUTION_TESTS_ACCESS_TOKEN = cast(str, os.getenv("SOLUTION_TESTS_ACCESS_TOKEN"))
GH_SOLUTION_OWNER = "artefactory-fr"
GH_SOLUTION_REPO_NAME = "school_of_data_tests"
GH_TESTS_FOLDER_NAME = "tests"
GH_API = "https://api.github.com/repos"
GH_ALL_ARTIFACT_ENDPOINT = "actions/artifacts"

git_integration = GithubIntegration(
    GH_APP_ID,
    GH_APP_KEY,
)

# Google Sheet
GSHEET_SA_JSON = cast(str, os.getenv("GSHEET_SA_JSON"))
GSHEET_SUMMARY_SPREADSHEET_ID = "1tzn73q_QhZ2gLAmZObRsE_JmD6yD6433uZBGc-Llsdk"
GSHEET_WORKSHEET_STUDENT = "students"
GSHEET_WORKSHEET_CHECK_VALIDATION_REPO = "check_validation_repo"
GSHEET_WORKSHEET_STUDENT_CHALLENGE_RESULT = "student_challenge_results"

GSHEET_DETAILS_SPREADSHEET_ID = "1pnRYrVngqtgdiMPXleS3EdLs4GY5jCTAJNSIXQofFH0"
GSHEET_HEADER_DETAILS_SPREADSHEET = [
    "login",
    "workflow_run_id",
    "created_at",
    "file_path",
    "script_name",
    "test_name",
    "outcome",
    "challenge_id",
    "info",
]

# Others
default_message: Dict[str, Dict[str, str]] = {
    "valid_repository": {
        "True": "Your folder `Test` is valid",
        "False": "Your folder `Test` has been modified and is no longer valid.",
    }
}

commit_sha_path: Dict[str, List[str]] = {
    "pull_request": ["pull_request", "head", "ref"],
    "pusher": ["ref"],
    "workflow_job": [],
}

CHALLENGE_DIR = "tests/tests/"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
