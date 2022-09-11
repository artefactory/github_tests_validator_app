from typing import Any, Dict, List, Tuple, Union

import logging

from github_tests_validator_app.config.config import CHALLENGE_DIR
from github_tests_validator_app.lib.connectors.github_connector import GitHubConnector
from github_tests_validator_app.lib.connectors.gsheet import GSheetConnector
from github_tests_validator_app.lib.models.pytest_result import PytestResult


def init_pytest_result_from_artifact(
    artifact: Dict[str, Any], workflow_run_id: int
) -> Union[PytestResult, None]:
    if not artifact:
        return None

    return PytestResult(
        DURATION=artifact["duration"],
        TOTAL_TESTS_COLLECTED=artifact["summary"]["collected"],
        TOTAL_PASSED_TEST=artifact["summary"]["passed"],
        TOTAL_FAILED_TEST=artifact["summary"]["failed"],
        DESCRIPTION_TEST_RESULTS=artifact["tests"],
        WORKFLOW_RUN_ID=workflow_run_id,
    )


def get_student_artifact(
    student_github_connector: GitHubConnector,
    gsheet: GSheetConnector,
    all_student_artifact: Dict[str, Any],
    payload: Dict[str, Any],
) -> Any:

    workflow_run_id = payload["workflow_job"]["run_id"]
    artifact_info = student_github_connector.get_artifact_info_from_artifacts_with_worflow_run_id(
        all_student_artifact["artifacts"], workflow_run_id
    )
    if not artifact_info:
        gsheet.add_new_student_result_summary(
            user=student_github_connector.user,
            result=PytestResult(),
            info="[ERROR]: Cannot find the artifact of Pytest result on GitHub user repository.",
        )
        logging.error(
            "[ERROR]: Cannot find the artifact of Pytest result on GitHub user repository."
        )
        return None

    # Read Artifact
    artifact_resp = student_github_connector.get_artifact(artifact_info)
    artifact = student_github_connector.get_artifact_from_format_zip_bytes(artifact_resp.content)
    if not artifact:
        gsheet.add_new_student_result_summary(
            user=student_github_connector.user,
            result=PytestResult(),
            info="[ERROR]: Cannot read the artifact of Pytest result on GitHub user repository.",
        )
        logging.error(
            "[ERROR]: Cannot read the artifact of Pytest result on GitHub user repository."
        )
        return None

    return artifact


def get_test_information(path: str) -> Tuple[str, str, str, str]:

    list_path_name = path.split("::")
    file_path = list_path_name[0]
    script_name = list_path_name[0].split("/")[-1]
    test_name = list_path_name[1]
    challenge_id = "-".join(
        [
            name[:2]
            for name in list_path_name[0].split(CHALLENGE_DIR)[1].split("/")
            if ".py" not in name
        ]
    )
    return challenge_id, file_path, script_name, test_name


def parsing_challenge_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    challenge_results = []
    for test in results:
        challenge_id, file_path, script_name, test_name = get_test_information(test["nodeid"])
        challenge_results.append(
            {
                "file_path": file_path,
                "script_name": script_name,
                "test_name": test_name,
                "challenge_id": challenge_id,
                "outcome": test["outcome"],
                "setup": test["setup"],
                "call": test["call"],
                "teardown": test["teardown"],
            }
        )

    return challenge_results


def send_student_challenge_results(
    student_github_connector: GitHubConnector, gsheet: GSheetConnector, payload: Dict[str, Any]
) -> None:

    # Get all artifacts
    all_student_artifact = student_github_connector.get_all_artifacts()
    if not all_student_artifact:
        message = f"[ERROR]: Cannot get all artifact on repository {student_github_connector.REPO_NAME} of user {student_github_connector.user.LOGIN}."
        if all_student_artifact["total_count"] == 0:
            message = f"[ERROR]: No artifact on repository {student_github_connector.REPO_NAME} of user {student_github_connector.user.LOGIN}."
        gsheet.add_new_student_result_summary(
            user=student_github_connector.user,
            result={},
            info=message,
        )
        logging.error(message)
        return

    # Get student artifact
    artifact = get_student_artifact(student_github_connector, gsheet, all_student_artifact, payload)
    if not artifact:
        return

    # Get summary student results
    pytest_result = init_pytest_result_from_artifact(artifact, payload["workflow_job"]["run_id"])
    # Send summary student results to Google Sheet
    gsheet.add_new_student_result_summary(
        user=student_github_connector.user,
        result=pytest_result,
        info="Result of student tests",
    )

    # Parsing artifact / challenge results
    challenge_results = parsing_challenge_results(artifact["tests"])
    # Send new detail results to Google Sheet
    gsheet.add_new_student_detail_results(
        user=student_github_connector.user,
        results=challenge_results,
        workflow_run_id=payload["workflow_job"]["run_id"],
    )
