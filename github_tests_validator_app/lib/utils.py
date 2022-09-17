from typing import Any, Dict, List, Union

import hashlib
import logging
from datetime import datetime

from github import ContentFile
from github_tests_validator_app.config.config import DATE_FORMAT
from github_tests_validator_app.lib.connectors.google_sheet import GSheetConnector
from github_tests_validator_app.lib.models.users import GitHubUser


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
    return GitHubUser(LOGIN=login, ID=id, URL=url, CREATED_AT=datetime.now().strftime(DATE_FORMAT))
