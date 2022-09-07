import pytest
from github_tests_validator_app.bin.github_repo_validation import get_event, get_student_branch


@pytest.mark.parametrize(
    "payload,expected",
    [
        ({}, ""),
        ({"unkown": "unkown"}, ""),
        ({"pull_request": "test"}, "pull_request"),
        ({"pusher": "test"}, "pusher"),
    ],
)
def test_get_event(payload, expected):
    assert get_event(payload) == expected


@pytest.mark.parametrize(
    "payload,trigger,expected",
    [
        ({"unknown": "unknown"}, None, None),
        ({"no_path": "no_path"}, "pull_request", None),
        ({"pull_request": {"head": {"unknown": "unknown"}}}, "pull_request", None),
        ({"pull_request": {"head": {"ref": "path"}}}, "pull_request", "path"),
        ({"ref": "path"}, "pusher", "path"),
    ],
)
def test_get_student_branch(payload, trigger, expected):
    assert get_student_branch(payload, trigger) == expected
