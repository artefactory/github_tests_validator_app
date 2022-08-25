from typing import Any

from config import TESTS_FOLDER_NAME
from github import ContentFile
from lib.connectors.github_connector import GitHubConnector


def compare_tests_folder(student_repo: GitHubConnector, solution_repo: GitHubConnector) -> Any:

    student_contents = student_repo.repo.get_contents(
        TESTS_FOLDER_NAME, ref=student_repo.BRANCH_NAME
    )

    if (
        isinstance(student_contents, ContentFile.ContentFile)
        and student_contents.type == "submodule"
    ):
        solution_last_commit = solution_repo.get_last_hash_commit()
        student_tests_commit = student_contents.sha
        return solution_last_commit == student_tests_commit

    student_hash_tests = student_repo.get_tests_hash(TESTS_FOLDER_NAME)
    solution_hash_tests = solution_repo.get_tests_hash(TESTS_FOLDER_NAME)
    return student_hash_tests == solution_hash_tests


def github_validator_repo(student_github: GitHubConnector, solution_github: GitHubConnector) -> Any:
    # Valide of repo
    tests_havent_changed = compare_tests_folder(student_github, solution_github)

    # Send results to GCP
    # FIXME

    # Results of challenges
    # FIXME
    return tests_havent_changed
