import hashlib

from github_tests_validator_app.constants import TESTS_FOLDER_NAME


def get_hash_files(contents):
    hash_sum = ""
    for content in contents:
        hash_sum += content.sha
    hash = hashlib.sha256()
    hash.update(hash_sum.encode())
    return str(hash.hexdigest())


def get_tests_hash(git_connection, owner, repo_name):
    repo = git_connection.get_repo(f"{owner}/{repo_name}")
    contents = repo.get_contents(TESTS_FOLDER_NAME)
    hash = get_hash_files(contents)
    return hash
