from typing import Any, Dict, List, Tuple, Union

import logging
from collections import defaultdict

from github_tests_validator_app.config.config import CHALLENGES_PATH
from github_tests_validator_app.lib.connectors.github_connector import GitHubConnector
from github_tests_validator_app.lib.connectors.google_sheet_connector import GSheet
from github_tests_validator_app.lib.pytest_result import PytestResult
from github_tests_validator_app.lib.users import GitHubUser


def init_pytest_result_from_artifact(artifact: Dict[str, Any]) -> Union[PytestResult, None]:
    if not artifact:
        return None

    # Get result of test

    return PytestResult(
        DURATION=artifact["duration"],
        TOTAL_TESTS_COLLECTED=artifact["summary"]["collected"],
        TOTAL_PASSED=artifact["summary"]["passed"],
        TOTAL_FAILED=artifact["summary"]["failed"],
        DESCRIPTION_TEST_RESULTS=artifact["tests"],
    )


def get_student_artifact(
    student_github_connector: GitHubConnector,
    gsheet: GSheet,
    all_student_artifact: Dict[str, Any],
    payload: Dict[str, Any],
) -> Any:
    workflow_run_id = payload["workflow_job"]["run_id"]
    artifact_info = student_github_connector.get_artifact_info_from_artifacts_with_worflow_run_id(
        all_student_artifact["artifacts"], workflow_run_id
    )
    if not artifact_info:
        gsheet.add_new_student_challenge_result(
            user=student_github_connector.user,
            result={},
            info="[ERROR]: Cannot find the artifact of Pytest result on GitHub user repository.",
        )
        logging.error(
            "[ERROR]: Cannot find the artifact of Pytest result on GitHub user repository."
        )
        return None

    ### Read Artifact
    artifact_resp = student_github_connector.get_artifact(artifact_info)
    artifact = student_github_connector.get_artifact_from_format_bytes_zip(artifact_resp.content)
    if not artifact:
        gsheet.add_new_student_challenge_result(
            user=student_github_connector.user,
            result={},
            info="[ERROR]: Cannot read the artifact of Pytest result on GitHub user repository.",
        )
        logging.error(
            "[ERROR]: Cannot read the artifact of Pytest result on GitHub user repository."
        )
        return None

    return artifact


def get_challenge_information_from_path(path: str) -> Tuple[str, str, str]:
    list_path_name = path.split(CHALLENGES_PATH)[1].split("/")
    challenge_id = "-".join([name[0:2] for name in list_path_name if not ".py" in name])
    challenge_name = path[-1].split(".py")[0].split("test_")[1]
    test_name = path[-1].split("::")[1]
    return challenge_name, challenge_id, test_name


def parsing_challenge_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    # challenge_results = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(str)))))
    challenge_results = []
    for test in results:
        challenge_name, challenge_id, test_name = get_challenge_information_from_path(
            test["nodeid"]
        )
        # if challenge_id in challenges_ref and challenge_name in challenges_ref[challenge_id]['name']:
        # challenge_results[challenge_id][challenge_name]["coef"] = challenges_ref[challenge_id]["coef"]
        # challenge_results[challenge_id][challenge_name]["tests"][test_name]["result"] = 1 if test.pop("outcome") == "passed" else 0

        # challenge_results[challenge_id][challenge_name]["tests"][test_name]["result"] = test.pop("outcome")
        # challenge_results[challenge_id][challenge_name]["tests"][test_name]["setup"] = test["setup"]
        # challenge_results[challenge_id][challenge_name]["tests"][test_name]["call"] = test["call"]
        # challenge_results[challenge_id][challenge_name]["tests"][test_name]["teardown"] = test["teardown"]
        info = {"setup": test["setup"], "call": test["call"], "teardown": test["teardown"]}

        challenge_results.append(
            {
                "id": challenge_id,
                "script": challenge_name,
                "test": test_name,
                "info": info,
                "result": test["outcome"],
                "path": test["nodeid"],
            }
        )

    # list_id = challenges_ref.keys() - challenge_results.keys()
    # for challenge_id in list_id:
    #     challenge_results[challenge_id][challenge_name]["coef"] = challenges_ref[challenge_id]["coef"]
    # breakpoint()
    return challenge_results


def get_final_results_challenges(challenge_results: Any) -> float:

    final_results = 0.0
    total_test = 0

    for challenge_id in challenge_results:
        for challenge_info in challenge_results[challenge_id].values():
            total_test += challenge_info["coef"]
            passed = sum(test["result"] for test in challenge_info["tests"].values()) / len(
                challenge_info["tests"]
            )
            passed = passed * challenge_info["coef"]
            final_results += passed

    final_results /= total_test
    return final_results


def send_student_challenge_results(
    student_github_connector: GitHubConnector, gsheet: GSheet, payload: Dict[str, Any]
) -> None:

    ### Get student artifact
    all_student_artifact = student_github_connector.get_all_artifacts()
    if not all_student_artifact:
        message = f"[ERROR]: Cannot get all artifact on repository {student_github_connector.REPO_NAME} of user {student_github_connector.user.LOGIN}."
        if all_student_artifact["total_count"] == 0:
            message = f"[ERROR]: No artifact on repository {student_github_connector.REPO_NAME} of user {student_github_connector.user.LOGIN}."
        gsheet.add_new_student_challenge_result(
            user=student_github_connector.user,
            result={},
            info=message,
        )
        logging.error(message)
        return

    artifact = get_student_artifact(student_github_connector, gsheet, all_student_artifact, payload)
    # challenges_ref = gsheet.get_challenge_coef()
    if not artifact:
        # Logging error
        return

    ### Parsing artifact / challenge results
    challenge_results = parsing_challenge_results(artifact["tests"])
    ### Get final results of student challenge results
    # final_result = get_final_results_challenges(challenge_results)

    # Get result
    pytest_result = init_pytest_result_from_artifact(artifact)
    ## Send Results to Google Sheet
    gsheet.add_new_student_challenge_result(
        user=student_github_connector.user,
        result=pytest_result,
        info="Result of student tests",
    )

    ### Delete artifact ?
