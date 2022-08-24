from typing import cast

import os

APP_ID = cast(str, os.getenv("GH_APP_ID"))

with open(
    "/Users/brunozheng/.certs/github/tests-validator-app-events.2022-08-22.private-key.pem"
) as f:
    APP_KEY = f.read()

# APP_KEY = cast(str, os.getenv("GH_APP_KEY"))
SOLUTION_TESTS_ACCESS_TOKEN = cast(str, os.getenv("SOLUTION_TESTS_ACCESS_TOKEN"))
SOLUTION_OWNER = "artefactory-fr"
SOLUTION_REPO_NAME = "school_of_data_tests"
TESTS_FOLDER_NAME = "tests"
