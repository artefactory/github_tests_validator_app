from typing import Union

from dataclasses import dataclass

from config import git_integration


@dataclass
class GitHubUser:

    LOGIN: str
    URL: Union[str, None] = None
    ID: Union[str, None] = None
    ACCESS_TOKEN: Union[str, None] = None

    def get_access_token(self, repo_name: str) -> str:

        self.ACCESS_TOKEN = git_integration.get_access_token(
            git_integration.get_installation(self.LOGIN, repo_name).id
        ).token
        return self.ACCESS_TOKEN
