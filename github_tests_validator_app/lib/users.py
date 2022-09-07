from typing import Union

from dataclasses import dataclass
from datetime import datetime

from github_tests_validator_app.config.config import DATE_FORMAT


@dataclass
class GitHubUser:

    LOGIN: str = ""
    URL: str = ""
    ID: str = ""
    CREATED_AT: str = datetime.now().strftime(DATE_FORMAT)
