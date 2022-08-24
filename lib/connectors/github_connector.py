import hashlib
from typing import List, Any
from github import Github, Repository, ContentFile

from lib.utils import get_hash_files

class GithubConnector():

    def __init__(self, token: str, owner: str, repo_name: str):
        self.OWNER = owner
        self.REPO_NAME = repo_name

        print(f"Connecting to Github as {owner} on {repo_name}...")
        self.connector = Github(login_or_token=token)
        print(f"Connecting to repo {repo_name} as {owner}...")
        self.repo = self.connector.get_repo(f"{owner}/{repo_name}")

    def get_repo(self, repo_name: str) -> Repository.Repository:
        self.REPO_NAME = repo_name
        print(f"Connecting to new repo {repo_name} as {self.OWNER}...")
        self.repo = self.connector.get_repo(f"{self.OWNER}/{repo_name}")
        return self.repo

    def get_last_hash_commit(self, branch_name: str) -> str:
        branch = self.repo.get_branch(branch_name)
        return branch.commit.sha

    def get_files_content(self, contents: Any) -> List[ContentFile.ContentFile]:
        files_content = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                files_content.append(file_content)
        return

    def get_tests_hash(self, folder_name: str) -> str:
        contents = self.repo.get_contents(folder_name)
        files_content = self.get_files_content(contents, self.repo)
        hash = get_hash_files(files_content)
        return hash

    def get_files_content(self, contents: Any) -> List[ContentFile.ContentFile]:
        files_content = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                files_content.append(file_content)
        return files_content
