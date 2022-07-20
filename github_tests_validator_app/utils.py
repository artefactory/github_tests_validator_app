from typing import Any, List

import hashlib

from github import ContentFile, Github, Repository
from github_tests_validator_app.constants import TESTS_FOLDER_NAME


def get_hash_files(contents: List[ContentFile.ContentFile]) -> str:
    hash_sum = ""
    for content in contents:
        hash_sum += content.sha
    hash = hashlib.sha256()
    hash.update(hash_sum.encode())
    return str(hash.hexdigest())


def get_tests_hash(token: str, owner: str, repo_name: str) -> str:
    git_connection = Github(login_or_token=token)
    repo = git_connection.get_repo(f"{owner}/{repo_name}")
    contents = repo.get_contents(TESTS_FOLDER_NAME)
    files_content = get_files_content(contents, repo)
    hash = get_hash_files(files_content)
    return hash


def get_files_content(contents: Any, repo: Repository.Repository) -> List[ContentFile.ContentFile]:
    if isinstance(contents, ContentFile.ContentFile):
        return [contents]
    else:
        files_content = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                files_content.append(file_content)
        return files_content
