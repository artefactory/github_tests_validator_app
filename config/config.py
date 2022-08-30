from typing import cast

import os

from github import GithubIntegration

# GitHub
APP_ID = cast(str, os.getenv("GH_APP_ID"))
APP_KEY = cast(str, os.getenv("GH_APP_KEY"))
SOLUTION_TESTS_ACCESS_TOKEN = cast(str, os.getenv("SOLUTION_TESTS_ACCESS_TOKEN"))
SOLUTION_OWNER = "artefactory-fr"
SOLUTION_REPO_NAME = "school_of_data_tests"

# Also github workflow
TESTS_FOLDER_NAME = "tests"

git_integration = GithubIntegration(
    APP_ID,
    APP_KEY,
)

# Google Sheet
GSHEET_SA_JSON = cast(str, os.getenv("GSHEET_SA_JSON"))
GSHEET_WORKSHEET_ID = "1tzn73q_QhZ2gLAmZObRsE_JmD6yD6433uZBGc-Llsdk"

# Others
default_message = {
    "valid_repository": {
        "True": "Your folder `Test` is valid",
        "False": "Your folder `Test` has been modified and is no longer valid.",
    }
}

commit_sha_path = {"pull_request": ["pull_request", "head", "ref"], "pusher": ["ref"]}
