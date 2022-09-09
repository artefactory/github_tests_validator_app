from typing import Any, Dict, Union

from dataclasses import dataclass


@dataclass
class PytestResult:

    DURATION: float
    TOTAL_TESTS_COLLECTED: int
    TOTAL_PASSED_TEST: int
    TOTAL_FAILED_TEST: int
    WORKFLOW_RUN_ID: int
    DESCRIPTION_TEST_RESULTS: Dict[str, Any]
    RESULT: Union[float, None] = None
