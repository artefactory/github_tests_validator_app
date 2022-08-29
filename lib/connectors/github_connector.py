from typing import Any, List

from github import ContentFile, Github, Repository
from lib.user import GitHubUser
from lib.utils import get_hash_files


class GitHubConnector:
    def __init__(self, user: GitHubUser, repo_name: str, branch_name: str):
        self.user = user
        self.REPO_NAME = repo_name
        self.BRANCH_NAME = branch_name

        print(f"Connecting to Github with user {self.user.LOGIN} on repo: {repo_name} ...")
        self.connector = Github(login_or_token=self.user.ACCESS_TOKEN, timeout=30)
        self.repo = self.connector.get_repo(f"{self.user.LOGIN}/{repo_name}")
        print("Done.")

    def get_repo(self, repo_name: str) -> Repository.Repository:
        self.REPO_NAME = repo_name
        print(f"Connecting to new repo: {repo_name} with user: {self.user.LOGIN} ...")
        self.repo = self.connector.get_repo(f"{self.user.LOGIN}/{repo_name}")
        print("Done.")
        return self.repo

    def get_last_hash_commit(self) -> str:
        branch = self.repo.get_branch(self.BRANCH_NAME)
        return branch.commit.sha

    def get_files_content(self, contents: Any) -> List[ContentFile.ContentFile]:
        files_content = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                files_content.append(file_content)
        return files_content

    def get_tests_hash(self, folder_name: str) -> str:
        contents = self.repo.get_contents(folder_name)
        files_content = self.get_files_content(contents)
        hash = str(get_hash_files(files_content))
        return hash
