from typing import Dict, List, cast

import logging
import os

import google.cloud.logging
from dotenv import load_dotenv

load_dotenv()

if os.getenv("LOGGING", "").replace("\r\n", "").replace("\r", "") == "GCP":
    logging_client = google.cloud.logging.Client()
    logging_client.get_default_handler()
    logging_client.setup_logging()
else:
    FORMAT = "%(asctime)s - %(levelname)s: %(message)s"
    DATEFMT = "%H:%M:%S"
    logging.basicConfig(
        format=FORMAT,
        level=logging.INFO,
        datefmt=DATEFMT,
    )

    if logging.getLogger("uvicorn") and logging.getLogger("uvicorn").handlers:
        logging.getLogger("uvicorn").removeHandler(logging.getLogger("uvicorn").handlers[0])


commit_ref_path: Dict[str, List[str]] = {
    "pull_request": ["pull_request", "head", "ref"],
    "pusher": ["ref"],
    "workflow_job": [],
}

# GitHub
GH_APP_ID = cast(str, os.getenv("GH_APP_ID", "")).replace("\r\n", "").replace("\r", "")
GH_APP_KEY = cast(str, os.getenv("GH_APP_KEY", ""))
GH_PAT = cast(str, os.getenv("GH_PAT", "")).replace("\r\n", "").replace("\r", "")

SQLALCHEMY_URI = cast(str, os.getenv("SQLALCHEMY_URI", "")).replace("\r\n", "").replace("\r", "").replace('"', '')
GH_TESTS_REPO_NAME = (
    cast(str, os.getenv("GH_TESTS_REPO_NAME", "")).replace("\r\n", "").replace("\r", "")
)
GH_TESTS_FOLDER_NAME = "validation_tests"
GH_WORKFLOWS_FOLDER_NAME = ".github/workflows"
GH_API = "https://api.github.com/repos"
GH_ALL_ARTIFACT_ENDPOINT = "actions/artifacts"

# Log message
default_message: Dict[str, Dict[str, Dict[str, str]]] = {
    "valid_repository": {
        "tests": {
            "True": "Your folder `.validation_tests/` is valid.",
            "False": "Your folder `.validation_tests/` has been modified and is no longer valid.",
        },
        "workflows": {
            "True": "Your folder `.github/workflows` is valid.",
            "False": "Your folder `.github/workflows` has been modified and is no longer valid.",
        },
    },
}

part_map = {
        "Part 1": [
            "validation_tests/test_01_git_101.py",
            "validation_tests/test_02_notebooks_to_scripts.py",
            "validation_tests/test_03_linting_and_formatting.py",
            "validation_tests/test_04_continuous_integration.py",
            "validation_tests/test_05_unit_testing.py",
            "validation_tests/test_06_code_documentation.py",
            "validation_tests/test_07_dependencies_and_venv.py"
            # "validation_tests/test_08_packaging.py"
        ],
        "Part 2": [
            "validation_tests/test_09_ci_cd_pipelines.py",
            "validation_tests/test_10_monitoring_and_alerting.py",
            "validation_tests/test_11_logging.py",
            "validation_tests/test_12_security_testing.py",
            "validation_tests/test_13_performance_optimization.py"
        ]
    }

base_tokens = {
    "Part 1" : [
        "FsQyRcFCNNzlUZpZ", "FyxfmqtAc8HCRLpx", "4VPhvLsrhJwfU3ee",
        "V9D2DaQgesfMs9Fc", "CJCIPgYQud6Io1jD", "mLFjjkXsxbTb0VCw",
        "9B8rMKEeR0p3gsJD", "i4M9CZuJQiwf8TKL", "JDn5CficECTa4JBN",
        "AjMJBlYQyA2bxuXg", "NZ2BNJDcUQ8BZYxX", "eb8YEgo8yoTenrVS",
        "WJbcGDT2Y7VjxNrZ", "oTzPvOupEY1eA3O9", "M0zAppk75VZEWAIx",
        "HjzUp5L9IzYhRzdj", "A04FC2reSxdIgHaK", "DXM297sx4alfByVx",
        "1G03TRqIamYRRNTF", "q78NrY9cESJESCBL"
    ],
    "Part 2" : [
        "Kh6MYcXAaQtWjKqn", "Diu0KzPzOU6Reced", "GB8DrumrkguJYDbm",
        "9Saz9603Gv7fQxh9", "4toXjiNOa2jQmveY", "S798d7fOXpExDtpR",
        "l3H2IALb5PziNqwZ", "1kaPHmA1I5o6fjyd", "032IKBCVNiWQdRYT",
        "TL2kMMZL5aK8j6rW", "gPdv1ahPY1Pd8Q9T", "4XdS6r53tJ01vFOa",
        "afHAgMIzQQI0HyDX", "SmINslEsh2OgAGGu", "RFFR6Z0Fmvsu5poQ",
        "hTfmdvk9uilnlkIN", "chyPPvztjsZiYgYE", "bxp7NA9uFwCtdtRL",
        "CzeYlSWdW2PgPpzk", "bcaTLaZQaCZx1zyJ"
    ]
}

required_checks = [
    "[Pytest] Pytest Result Validation",
    "[Integrity] Test Folder Validation",
    "[Integrity] Workflow Folder Validation"
]