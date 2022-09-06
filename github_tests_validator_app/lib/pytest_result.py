from typing import Any, Dict, Union

from dataclasses import dataclass


@dataclass
class PytestResult:

    DURATION: float
    TOTAL_TESTS_COLLECTED: int
    TOTAL_PASSED: int
    TOTAL_FAILED: int
    DESCRIPTION_TEST_RESULTS: Dict[str, Any]
    RESULT: Union[float, None] = None
