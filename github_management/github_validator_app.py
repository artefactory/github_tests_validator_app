from github import GithubIntegration
from github_management.constants import (
    APP_ID,
    APP_KEY,
    SOLUTION_OWNER,
    SOLUTION_REPO_NAME,
    SOLUTION_TESTS_ACCESS_TOKEN,
    TESTS_FOLDER_NAME,
)
from github_management.utils import compare_tests_folder, get_repo

git_integration = GithubIntegration(
    APP_ID,
    APP_KEY,
)

triggers = {
    'pull_request': ['pull_request', 'head', 'ref'],
    'pusher': ['ref']
}

def get_student_branch(payload: dict = None):
    for trigger in triggers:
        if trigger in payload:
            branch = payload
            path = triggers[trigger]
            while path:
                branch = branch[path.pop(0)]
            return branch
    return None

def get_student_repo(payload: dict = None):
    owner = payload["repository"]["owner"]["login"]
    repo_name = payload["repository"]["name"]
    token = git_integration.get_access_token(
        git_integration.get_installation(owner, repo_name).id
    ).token

    return get_repo(token, owner, repo_name)

def github_validator_repo(payload: dict):
    student_repo = get_student_repo(payload)
    student_branch = get_student_branch(payload)
    if student_branch is None:
        # Log error
        # FIXME
        # Archive the payload
        # FIXME
        print('Could\'nt find the student commit, maybe the trigger is not managed')
        return False

    solution_repo = get_repo(SOLUTION_TESTS_ACCESS_TOKEN, SOLUTION_OWNER, SOLUTION_REPO_NAME)

    # Valide of repo
    tests_havent_changed = compare_tests_folder(student_repo, solution_repo, student_branch)

    # Send results to GCP
    # FIXME

    # Results of challenges
    # FIXME
    return tests_havent_changed
