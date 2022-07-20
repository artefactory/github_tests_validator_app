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


def get_tests_hash(repo: Repository.Repository) -> str:
    contents = repo.get_contents(TESTS_FOLDER_NAME)
    files_content = get_files_content(contents, repo)
    hash = get_hash_files(files_content)
    return hash


def get_files_content(contents: Any, repo: Repository.Repository) -> List[ContentFile.ContentFile]:
    files_content = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            files_content.append(file_content)
    return files_content


def get_repo(token: str, owner: str, repo_name: str) -> Repository.Repository:
    git_connection = Github(login_or_token=token)
    repo = git_connection.get_repo(f"{owner}/{repo_name}")
    return repo


def get_last_hash_commit(repo: Repository.Repository, branch_name: str) -> str:
    branch = repo.get_branch(branch_name)
    return branch.commit.sha


def compare_tests_folder(
    student_repo: Repository.Repository, solution_repo: Repository.Repository
) -> bool:
    student_contents = student_repo.get_contents(TESTS_FOLDER_NAME)

    if (
        isinstance(student_contents, ContentFile.ContentFile)
        and student_contents.type == "submodule"
    ):
        solution_last_commit = get_last_hash_commit(solution_repo, "main")
        student_tests_commit = student_contents.sha
        return solution_last_commit == student_tests_commit

    student_hash_tests = get_tests_hash(student_repo)
    solution_hash_tests = get_tests_hash(solution_repo)

    return student_hash_tests == solution_hash_tests
