from typing import Any, Dict, List, Optional

import re
import hashlib
import logging
import random
from datetime import datetime

from github import ContentFile, GithubException
from github_tests_validator_app.lib.connectors.sqlalchemy_client import User



def get_hash_files(contents: List[ContentFile.ContentFile]) -> str:
    hash = hashlib.sha256()

    for content in contents:
        if content.type == 'file':
            file_content = content.decoded_content  # Gets the file's content as bytes
            logging.info(f"Hashing content for file: {content.path}, Content length: {len(file_content)}")
            hash.update(file_content)
        else:
            logging.info(f"Hashing submodule/directory SHA for: {content.path}, SHA: {content.sha}")
            hash.update(content.sha.encode())

    hash_value = str(hash.hexdigest())
    logging.info(f"Generated hash value: {hash_value}")
    return hash_value

def init_github_user_from_github_event(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:

    if not "sender" in data:
        return None

    login = data["sender"]["login"]
    id = data["sender"]["id"]
    url = data["sender"]["url"]
    return dict(id=id, organization_or_user=login, url=url, created_at=datetime.now())


def pull_requested_test_results(
    tests_results_json: Dict[str, Any],
    payload: Dict[str, Any],
    github_event: str,
    user_github_connector
) -> str:
    """
    Retrieve and format only the test results specific to the PR name,
    handling both 'pull_request' and 'push' events.
    """
    if not tests_results_json:
        return "No test results found."

    # Determine the pull request title based on the event type
    if github_event == "pull_request":
        pull_request_title = payload["pull_request"]["title"]
    elif github_event == "pusher":
        # For push events, retrieve the PR title by querying GitHub
        branch = payload["ref"].replace("refs/heads/", "")# Extract branch name from the ref
        logging.info(f"branch = {branch}")
        prs = user_github_connector.repo.get_pulls(state="open", head=f"{user_github_connector.repo.owner.login}:{branch}")
        logging.info(f"PRS = {prs}")
        if prs.totalCount > 0:
            pull_request_title = prs[0].title
            logging.info(f"TITLE = {pull_request_title}")
        else:
            return "No associated pull request found for this branch."
    else:
        return "Unsupported event type."

    # Extract the PR name and determine the test prefix
    match = re.match(r"(\d+):", pull_request_title)
    if not match:
        return "No matching test prefix found for this PR."

    current_exercice = int(match.group(1))
    test_prefixes = [
        f"validation_tests/test_{str(i).zfill(2)}" for i in range(current_exercice + 1)
    ]

    # Filter and format test results specific to the PR name
    test_failed = 0
    filtered_messages = []
    for test in tests_results_json.get("tests", []):
        nodeid = test.get("nodeid", "Unknown test")
        for prefix in test_prefixes:
            if nodeid.startswith(prefix):
                outcome = test.get("outcome", "unknown")
                if outcome == "failed":
                    test_failed += 1
                message = test.get("call", {}).get("crash", {}).get("message", "No message available\n")
                traceback = test.get("call", {}).get("crash", {}).get("traceback", "No traceback available\n")
                filtered_messages.append(
                    f"- **{nodeid}**:\n\n"
                    f"  - **Outcome**: {outcome}\n"
                    f"  - **Message**:\n```\n{message}```\n"
                    f"  - **Traceback**:\n```\n{traceback}```\n"
                )
                break

    if filtered_messages:
        return "\n".join(filtered_messages), test_failed
    else:
        return "No matching test results for this PR.", test_failed


def strip_ansi_escape_codes(text: str) -> str:
    """
    Removes ANSI escape codes from the given text.
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def validate_checks_and_assign_token(sha, tokens, user_github_connector, required_checks):
    try:
        # Fetch check runs for the given SHA
        check_runs = user_github_connector.repo.get_commit(sha).get_check_runs()
        for check_name in required_checks:
            # Filter for matching check runs
            matching_checks = [
                check for check in check_runs if check.name == check_name
            ]
            if not matching_checks:
                logging.warning(f"Required check '{check_name}' not found.")
                return None, None

            for check in matching_checks:
                logging.info(f"Validating check '{check.name}' with status: {check.conclusion}")
                if check.conclusion != "success":
                    logging.warning(f"Check '{check.name}' did not pass.")
                    return None, None

        # If all checks are successful, assign a token
        for part, token_list in tokens.items():
            if token_list:
                token = random.choice(token_list)
                return part, token

    except GithubException as e:
        logging.error(f"Error fetching check runs for SHA {sha}: {e}")
        return None, None

    return None, None