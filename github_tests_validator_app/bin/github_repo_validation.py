from typing import Any, Dict, List, Union

import logging

from github import ContentFile
from github_tests_validator_app.config import (
    GH_PAT,
    GH_TESTS_FOLDER_NAME,
    GH_TESTS_REPO_NAME,
    GH_WORKFLOWS_FOLDER_NAME,
    commit_ref_path,
    default_message,
    base_tokens,
    required_checks
)

from github_tests_validator_app.lib.utils import (
    pull_requested_test_results,
    validate_and_assign_token
)

from github_tests_validator_app.lib.connectors.github_client import GitHubConnector
from github_tests_validator_app.lib.connectors.sqlalchemy_client import SQLAlchemyConnector, User


def get_event(payload: Dict[str, Any]) -> str:
    for event in commit_ref_path:
        if event in payload:
            return str(event)
    return ""


def get_user_branch(payload: Dict[str, Any], trigger: Union[str, None] = None) -> Any:
    trigger = get_event(payload) if not trigger else trigger
    if not trigger:
        logging.error("Couldn't find the user branch, maybe the trigger is not managed")
        return None

    path = commit_ref_path[trigger].copy()
    branch = payload
    while path:

        try:
            branch = branch[path.pop(0)]
        except KeyError as key_err:
            logging.error(key_err)
            return None
        except Exception as err:
            logging.error(err)
            return None

    return branch


def get_user_github_connector(
    user_data: Dict[str, Any], payload: Dict[str, Any]
) -> Union[GitHubConnector, None]:

    if not user_data:
        return None

    github_user_branch = get_user_branch(payload)
    if github_user_branch is None:
        return None

    return GitHubConnector(user_data, payload["repository"]["full_name"], github_user_branch)


def compare_folder(
    user_github: GitHubConnector, solution_repo: GitHubConnector, folder: str
) -> Any:

    logging.info(f"BRANCH NAME: {user_github.BRANCH_NAME}")
    user_contents = user_github.repo.get_contents(folder, ref=user_github.BRANCH_NAME)

    if isinstance(user_contents, ContentFile.ContentFile) and user_contents.type == "submodule":
        solution_last_commit = solution_repo.get_last_hash_commit()
        user_commit = user_contents.sha
        return solution_last_commit == user_commit

    user_hash = user_github.get_hash(folder)
    solution_hash = solution_repo.get_hash(folder)
    logging.info(f"user_hash = {user_hash}")
    logging.info(f"solution_hash = {solution_hash}")
    return user_hash == solution_hash


def validate_github_repo(
    user_github_connector: GitHubConnector,
    sql_client: SQLAlchemyConnector,
    payload: Dict[str, Any],
    event: str,
) -> None:

    logging.info(f"Connecting to TESTS repo : {GH_TESTS_REPO_NAME}")

    if user_github_connector.repo.parent:
        original_repo_name = user_github_connector.repo.parent.full_name
        logging.info(f"Connecting to ORIGINAL repo : {original_repo_name}")
    else:
        original_repo_name = user_github_connector.repo.full_name
        logging.info(f"Repository '{original_repo_name}' is not a fork, connecting to the same repository.")
        
    tests_github_connector = GitHubConnector(
        user_data=user_github_connector.user_data,
        repo_name=GH_TESTS_REPO_NAME
        if GH_TESTS_REPO_NAME
        else original_repo_name,
        branch_name="feat/ci_workflow",
        access_token=GH_PAT,
    )
    
    original_github_connector = GitHubConnector(
        user_data=user_github_connector.user_data,
        repo_name=original_repo_name,
        branch_name="feat/ci_workflow",
        access_token=GH_PAT,
    )
    
    if not tests_github_connector:
        sql_client.add_new_repository_validation(
            user_github_connector.user_data,
            False,
            payload,
            event,
            "[ERROR]: cannot get the tests github repository.",
        )
        logging.error("[ERROR]: cannot get the tests github repository.")
        return
    
    if not original_github_connector:
        sql_client.add_new_repository_validation(
            user_github_connector.user_data,
            False,
            payload,
            event,
            "[ERROR]: cannot get the original github repository.",
        )
        logging.error("[ERROR]: cannot get the original github repository.")
        return

    workflows_havent_changed = compare_folder(
        user_github_connector, original_github_connector, GH_WORKFLOWS_FOLDER_NAME
    )

    tests_havent_changed = compare_folder(
        user_github_connector, tests_github_connector, GH_TESTS_FOLDER_NAME
    )

    tests_conclusion = "success" if tests_havent_changed else "failure"
    tests_message = default_message["valid_repository"]["tests"][str(tests_havent_changed)]

    workflows_conclusion = "success" if workflows_havent_changed else "failure"
    workflows_message = default_message["valid_repository"]["workflows"][
        str(workflows_havent_changed)
    ]

    # Fetch the test results JSON from GitHub Actions artifact
    pytests_results_json = user_github_connector.get_tests_results_json()

    if pytests_results_json is None:
        logging.error("Validation failed due to missing or invalid test results artifact.")
        pytest_result_message = "No test results found."
        pytest_result_conclusion = "faillure"
    else:
        failed_tests = pull_requested_test_results(
            tests_results_json=pytests_results_json,
            payload=payload,
            github_event=event,
            user_github_connector=user_github_connector
        )
        pytest_result_conclusion = "failure" if failed_tests[1] > 0 else "success"


    sql_client.add_new_repository_validation(
        user_github_connector.user_data,
        workflows_havent_changed,
        payload,
        event,
        default_message["valid_repository"]["workflows"][str(workflows_havent_changed)],
    )
    
    sql_client.add_new_repository_validation(
        user_github_connector.user_data,
        tests_havent_changed,
        payload,
        event,
        default_message["valid_repository"]["tests"][str(tests_havent_changed)],
    )


    if event == "pull_request":
        try :
            # Create a Check Run with detailed test results in case of failure
            user_github_connector.repo.create_check_run(
                name="[Integrity] Test Folder Validation",
                head_sha=payload["pull_request"]["head"]["sha"],
                status="completed",
                conclusion=tests_conclusion,
                output={
                    "title": "Test Folder Validation Result",
                    "summary": tests_message,
                }
            )
            user_github_connector.repo.create_check_run(
                name="[Integrity] Workflow Folder Validation",
                head_sha=payload["pull_request"]["head"]["sha"],
                status="completed",
                conclusion=workflows_conclusion,
                output={
                    "title": "Workflow Folder Validation Result",
                    "summary": workflows_message,
                }
            )
            pytest_result_message = pull_requested_test_results(
                tests_results_json=pytests_results_json,
                payload=payload,
                github_event=event,
                user_github_connector=user_github_connector
            )
            user_github_connector.repo.create_check_run(
                name="[Pytest] Pytest Result Validation",
                head_sha=payload["pull_request"]["head"]["sha"],
                status="completed",
                conclusion=pytest_result_conclusion,
                output={
                    "title": "Pytest Validation Result",
                    "summary": pytest_result_message[0],
                }
            )
        except Exception as e :
            logging.error(f"Error creating check run: {e}")

        # All exercice need to be validated for -> Token
        part, token = validate_and_assign_token(sha=payload["pull_request"]["head"]["sha"],
                                                tokens=base_tokens,
                                                user_github_connector=user_github_connector,
                                                required_checks=required_checks)

        if part and token:
            pr_number = payload["pull_request"]["number"]
            comment_message = (
                f"🎉 Congratulations! You've validated all exercises for {part}. "
                f"Here is your token: `{token}`"
            )
            # Post a comment in the PR
            user_github_connector.repo.get_pull(pr_number).create_issue_comment(comment_message)
            logging.info(f"Posted comment to PR #{pr_number}: {comment_message}")
        else:
            logging.info("Not all exercises are validated. No token assigned.")

    elif event == "pusher":
        # Check if there is already an open PR
        gh_branch = payload["ref"].replace("refs/heads/", "")
        gh_prs = user_github_connector.repo.get_pulls(
            state="open",
            head=f"{user_github_connector.repo.owner.login}:{gh_branch}"
        )
        logging.info(f"HEAD SHA for check runs: {payload['after']}")

        if gh_prs.totalCount > 0:
            gh_pr = gh_prs[0] # Get first matching PR
            if gh_pr.head.sha == payload["after"]:
                logging.info("SHA matches an open PR; skipping duplicate processing.")
            
        try :    
            user_github_connector.repo.create_check_run(
                name="[Integrity] Test Folder Validation",
                head_sha=payload["after"],
                status="completed",
                conclusion=tests_conclusion,
                output={
                    "title": "Test Folder Validation Result",
                    "summary": tests_message,
                }
            )
            user_github_connector.repo.create_check_run(
                name="[Integrity] Workflow Folder Validation",
                head_sha=payload["after"],
                status="completed",
                conclusion=workflows_conclusion,
                output={
                    "title": "Workflow Folder Validation Result",
                    "summary": workflows_message,
                }
            )
            pytest_result_message = pull_requested_test_results(
                tests_results_json=pytests_results_json,
                payload=payload,
                github_event=event,
                user_github_connector=user_github_connector
            )
            user_github_connector.repo.create_check_run(
                name="[Pytest] Pytest Result Validation",
                head_sha=payload["after"],
                status="completed",
                conclusion=pytest_result_conclusion,
                output={
                    "title": "Pytest Validation Result",
                    "summary": pytest_result_message[0],
                }
            )
        except Exception as e:
            logging.error(f"Error creating check run: {e}")

        # All exercice need to be validated for -> Token
        part, token = validate_and_assign_token(sha=payload["ref"],
                                                tokens=base_tokens,
                                                user_github_connector=user_github_connector,
                                                required_checks=required_checks)

        if part and token:
            branch_ref = payload["ref"]  # e.g., 'refs/heads/branch_name'
            
            # Retrieve the pull request associated with the branch
            open_prs = user_github_connector.repo.get_pulls(state="open", head=f"{user_github_connector.repo.owner.login}:{branch_ref}")
            if open_prs.totalCount == 1:
                pr_number = open_prs[0].number
                comment_message = (
                    f"🎉 Congratulations! You've validated all exercises for {part}. "
                    f"Here is your token: `{token}`"
                )
                # Post a comment in the PR
                open_prs[0].create_issue_comment(comment_message)
                logging.info(f"Posted comment to PR #{pr_number}: {comment_message}")
            else:
                logging.warning(f"Could not determine a single open PR for branch {branch_ref}.")
        else:
            logging.info("Not all exercises are validated. No token assigned.")