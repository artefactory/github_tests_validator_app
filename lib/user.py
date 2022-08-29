from typing import Union

from dataclasses import dataclass
from datetime import datetime

from config import git_integration


@dataclass
class GitHubUser:

    LOGIN: str
    URL: str = ""
    ID: str = ""
    ACCESS_TOKEN: Union[str, None] = None
    CREATED_AT: str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def get_access_token(self, repo_name: str) -> str:
        self.ACCESS_TOKEN = git_integration.get_access_token(
            git_integration.get_installation(self.LOGIN, repo_name).id
        ).token
        return self.ACCESS_TOKEN
