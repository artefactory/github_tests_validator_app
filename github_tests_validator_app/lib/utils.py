from typing import Any, Dict, List, Union

import hashlib

from github import ContentFile
from github_tests_validator_app.lib.users import GitHubUser


def get_hash_files(contents: List[ContentFile.ContentFile]) -> str:
    hash_sum = ""
    for content in contents:
        hash_sum += content.sha
    hash = hashlib.sha256()
    hash.update(hash_sum.encode())
    return str(hash.hexdigest())


def init_github_user_from_github_event(data: Dict[str, Any]) -> Union[GitHubUser, None]:

    if not "repository" in data or not "owner" in data["repository"]:
        return None

    login = data["repository"]["owner"].get("login", None)
    id = data["repository"]["owner"].get("id", None)
    url = data["repository"]["owner"].get("url", None)
    return GitHubUser(LOGIN=login, ID=id, URL=url)
