from typing import Any, Dict, Union

from dataclasses import dataclass, field


@dataclass
class PytestResult:

    DURATION: float = 0.0
    TOTAL_TESTS_COLLECTED: int = 0
    TOTAL_PASSED_TEST: int = 0
    TOTAL_FAILED_TEST: int = 0
    WORKFLOW_RUN_ID: int = 0
    DESCRIPTION_TEST_RESULTS: Dict[str, Any] = field(default_factory=Dict[str, Any])
    RESULT: Union[float, None] = None
