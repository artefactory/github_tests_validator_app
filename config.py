from typing import cast

import os

from github import GithubIntegration

APP_ID = cast(str, os.getenv("GH_APP_ID"))
APP_KEY = cast(str, os.getenv("GH_APP_KEY"))
SOLUTION_TESTS_ACCESS_TOKEN = cast(str, os.getenv("SOLUTION_TESTS_ACCESS_TOKEN"))
SOLUTION_OWNER = "artefactory-fr"
SOLUTION_REPO_NAME = "school_of_data_tests"
TESTS_FOLDER_NAME = "tests"
GSHEET_SA_JSON = cast(str, os.getenv("GSHEET_SA_JSON"))


git_integration = GithubIntegration(
    APP_ID,
    APP_KEY,
)
