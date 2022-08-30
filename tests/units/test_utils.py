from unittest.mock import PropertyMock

import pytest
from github import ContentFile
from lib.user import GitHubUser
from lib.utils import get_hash_files, init_github_user_from_github_event


@pytest.mark.parametrize(
    "contents,expected",
    [
        ([""], "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        (["1", "2", "3", "4"], "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"),
        (
            ["abc", "def", "ghi", "klmn"],
            "00c0780a668d95d2052f927c4fd5b4bbc35feaaf6a3e3c54b048eee29d0eef6a",
        ),
    ],
)
def test_get_hast_files(mocker, contents, expected):
    mocker.patch(
        "github.ContentFile.ContentFile.sha",
        new_callable=PropertyMock,
        side_effect=contents,
    )
    assert get_hash_files([ContentFile.ContentFile for _ in contents]) == expected


@pytest.mark.parametrize(
    "contents,expected",
    [
        (
            {"repository": {"owner": {"login": "test", "id": "1234", "url": "url"}}},
            GitHubUser(LOGIN="test", ID="1234", URL="url"),
        ),
        (
            {"repository": {"owner": {"login": None, "id": None, "url": None}}},
            GitHubUser(LOGIN=None, ID=None, URL=None),
        ),
        ({}, None),
    ],
)
def test_init_github_user_from_github_event(contents, expected):
    github_user = init_github_user_from_github_event(contents)
    assert isinstance(github_user, type(expected))
    if isinstance(github_user, GitHubUser):
        assert (
            github_user.LOGIN == expected.LOGIN
            and github_user.ID == expected.ID
            and github_user.URL == expected.URL
        )
