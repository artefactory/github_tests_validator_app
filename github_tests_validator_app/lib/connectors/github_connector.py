from typing import Any, Dict, List, Union

import io
import json
import logging
import zipfile

import requests
from github import ContentFile, Github, GithubIntegration, Repository
from github_tests_validator_app.config.config import (
    GCP_PROJECT_ID,
    GH_ALL_ARTIFACT_ENDPOINT,
    GH_API,
    GH_APP_ID,
    GH_APP_KEY_NAME,
)
from github_tests_validator_app.lib.connectors.google_secret_manager import GSecretManager
from github_tests_validator_app.lib.models.users import GitHubUser
from github_tests_validator_app.lib.utils import get_hash_files


class GitHubConnector:
    def __init__(
        self,
        user: GitHubUser,
        repo_name: str,
        branch_name: str,
        access_token: Union[str, None] = None,
    ):
        self.user = user
        self.REPO_NAME = repo_name
        self.BRANCH_NAME = branch_name
        self.ACCESS_TOKEN = access_token

        logging.info(f"Connecting to Github with user {self.user.LOGIN} on repo: {repo_name} ...")
        if not access_token:
            self.set_git_integration()
            self.set_access_token(repo_name)
        self.connector = Github(login_or_token=self.ACCESS_TOKEN, timeout=30)
        self.repo = self.connector.get_repo(f"{self.user.LOGIN}/{repo_name}")
        logging.info("Done.")

    def set_git_integration(self) -> None:

        gsecret_manager = GSecretManager(GCP_PROJECT_ID)
        github_app_key = gsecret_manager.get_access_secret_version(GH_APP_KEY_NAME)

        self.git_integration = GithubIntegration(
            GH_APP_ID,
            github_app_key,
        )

    def set_access_token(self, repo_name: str) -> None:
        self.ACCESS_TOKEN = self.git_integration.get_access_token(
            self.git_integration.get_installation(self.user.LOGIN, repo_name).id
        ).token

    def get_repo(self, repo_name: str) -> Repository.Repository:
        self.REPO_NAME = repo_name
        logging.info(f"Connecting to new repo: {repo_name} with user: {self.user.LOGIN} ...")
        self.repo = self.connector.get_repo(f"{self.user.LOGIN}/{repo_name}")
        logging.info("Done.")
        return self.repo

    def get_last_hash_commit(self) -> str:
        branch = self.repo.get_branch(self.BRANCH_NAME)
        return branch.commit.sha

    def get_files_content(self, contents: Any) -> List[ContentFile.ContentFile]:
        files_content = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                files_content.append(file_content)
        return files_content

    def get_tests_hash(self, folder_name: str) -> str:
        contents = self.repo.get_contents(folder_name)
        files_content = self.get_files_content(contents)
        hash = str(get_hash_files(files_content))
        return hash

    def get_all_artifacts(self) -> Union[requests.models.Response, Any]:
        url = "/".join([GH_API, self.user.LOGIN, self.REPO_NAME, GH_ALL_ARTIFACT_ENDPOINT])
        headers = self._get_headers()
        response = self._request_data(url, headers=headers)
        return response

    def get_artifact_info_from_artifacts_with_worflow_run_id(
        self, artifacts: List[Dict[str, Any]], worflow_run_id: int
    ) -> Union[None, Dict[str, Any]]:
        for artifact in artifacts:
            if artifact["workflow_run"]["id"] == worflow_run_id:
                return artifact
        return None

    def get_artifact_from_format_zip_bytes(self, artifact_content: bytes) -> Any:
        z = zipfile.ZipFile(io.BytesIO(artifact_content))
        f = z.read(z.namelist()[0])
        decode = f.decode("utf-8")
        return json.loads(decode)

    def get_artifact(self, artifact_info: Dict[str, Any]) -> Union[requests.models.Response, Any]:
        artifact_id = str(artifact_info["id"])
        archive_format = "zip"
        url = "/".join(
            [
                GH_API,
                self.user.LOGIN,
                self.REPO_NAME,
                GH_ALL_ARTIFACT_ENDPOINT,
                artifact_id,
                archive_format,
            ]
        )
        headers = self._get_headers()
        response = self._request_data(url, headers=headers, dict_format=False)
        return response

    def _get_headers(self) -> Dict[str, str]:
        if not self.ACCESS_TOKEN:
            self.set_access_token(self.REPO_NAME)

        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.ACCESS_TOKEN}",
        }

    def _request_data(
        self,
        url: str,
        headers: Dict[str, Any],
        params: Union[Dict[str, Any], None] = None,
        dict_format: Union[bool, None] = True,
    ) -> Union[requests.models.Response, Any]:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        if dict_format:
            return response.json()
        return response
