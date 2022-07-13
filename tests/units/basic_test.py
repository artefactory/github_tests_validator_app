from github_tests_validator_app.utils import get_hash_files


def test_length_hash():
    assert len(get_hash_files("")) == 64
