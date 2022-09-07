from typing import Union

from dataclasses import dataclass
from datetime import datetime

from github_tests_validator_app.config.config import DATE_FORMAT, git_integration


@dataclass
class GitHubUser:

    LOGIN: str = ""
    URL: str = ""
    ID: str = ""
    ACCESS_TOKEN: Union[str, None] = None
    CREATED_AT: str = datetime.now().strftime(DATE_FORMAT)

    def get_access_token(self, repo_name: str) -> str:
        self.ACCESS_TOKEN = git_integration.get_access_token(
            git_integration.get_installation(self.LOGIN, repo_name).id
        ).token
        return self.ACCESS_TOKEN
