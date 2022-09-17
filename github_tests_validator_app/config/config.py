from typing import Dict, cast

import os

import yaml

# GitHub
GH_APP_ID = cast(str, os.getenv("GH_APP_ID", None))
GH_SOLUTION_OWNER = "artefactory-fr"
GH_SOLUTION_REPO_NAME = "school_of_data_tests"
GH_TESTS_FOLDER_NAME = "tests"
GH_API = "https://api.github.com/repos"
GH_ALL_ARTIFACT_ENDPOINT = "actions/artifacts"

# GCP
GCP_PROJECT_ID = "school-of-data-github-app"

# Google Secrets
GH_APP_KEY_NAME = "github_test_validator_app_key"
GH_ACCESS_TOKEN_NAME = "github_personal_access_token"

# Google Drive
GDRIVE_MAIN_DIRECTORY_NAME = "school_of_data_results"

# Google Sheet
GDRIVE_HIERARCHY_PATH = "github_tests_validator_app/config/data/gdrive_hierarchy.yml"
with open(GDRIVE_HIERARCHY_PATH) as file:
    data = yaml.safe_load(file)

GDRIVE_SUMMARY_SPREADSHEET = data["gdrive_summary_spreadsheet"]
GSHEET_DETAILS_SPREADSHEET = data["gsheet_details_spreadsheet"]

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
USER_SHARE = os.getenv("USER_SHARE", "").split(",")
