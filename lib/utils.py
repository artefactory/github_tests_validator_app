from typing import Any, Dict, List

import hashlib

from github import ContentFile
from lib.user import GitHubUser


def get_hash_files(contents: List[ContentFile.ContentFile]) -> str:
    hash_sum = ""
    for content in contents:
        hash_sum += content.sha
    hash = hashlib.sha256()
    hash.update(hash_sum.encode())
    return str(hash.hexdigest())


def get_github_user(data: Dict[str, Any]) -> GitHubUser:
    login = data["repository"]["owner"]["login"]
    id = data["repository"]["owner"]["id"]
    url = data["repository"]["owner"]["url"]
    return GitHubUser(LOGIN=login, ID=str(id), URL=url)
