from typing import Any, Dict, List, Union

import os
import io
import json
import time
import logging
import zipfile

import requests
from github import Auth
from github import ContentFile, Github, GithubIntegration, Repository, UnknownObjectException
from github_tests_validator_app.config import (
    GH_ALL_ARTIFACT_ENDPOINT,
    GH_API,
    GH_APP_ID,
    GH_APP_KEY,
)
from github_tests_validator_app.lib.utils import get_hash_files


class GitHubConnector:
    def __init__(
        self,
        user_data: Dict[str, Any],
        repo_name: str,
        branch_name: str,
        access_token: Union[str, None] = None,
    ) -> None:
        self.user_data = user_data
        self.REPO_NAME = repo_name
        self.BRANCH_NAME = branch_name
        self.ACCESS_TOKEN = access_token

        logging.info(
            f"Connecting to Github with user {self.user_data['organization_or_user']} on repo: {repo_name} ..."
        )
        if not access_token:
            logging.info("No access token provided, trying to get one ...")
            self.set_git_integration()
            self.set_access_token(repo_name)

        logging.info(f"Access token: {self.ACCESS_TOKEN[:10]}... (truncated for security)")
        
        try:
            self.connector = Github(login_or_token=self.ACCESS_TOKEN, timeout=30)
            self.repo = self.connector.get_repo(f"{repo_name}")
            logging.info(f"repo_name = {repo_name} and repo = {self.repo}")
            logging.info(f"Successfully connected to repo: {repo_name}")
        except Exception as e:
            logging.error(f"Failed to connect to repo: {repo_name}, error: {e}")
            raise e

    def set_git_integration(self) -> None:
        self.git_integration = GithubIntegration(
            auth=Auth.AppAuth(app_id=GH_APP_ID, private_key=GH_APP_KEY)
        )

    def set_access_token(self, repo_name: str) -> None:
        self.ACCESS_TOKEN = self.git_integration.get_access_token(
            installation_id=self.git_integration.get_installation(
                repo_name.split("/")[0], repo_name.split("/")[1]
            ).id
        ).token

    def get_repo(self, repo_name: str) -> Repository.Repository:
        self.REPO_NAME = repo_name
        self.repo = self.connector.get_repo(f"{repo_name}")
        logging.info("Done.")
        return self.repo

    def get_last_hash_commit(self) -> str:
        branch = self.repo.get_branch(self.BRANCH_NAME)
        logging.info(f"BRANCH NAME: {self.BRANCH_NAME}")
        return branch.commit.sha

    def get_files_content(self, contents: Any) -> List[ContentFile.ContentFile]:
        files_content = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                logging.info(f"Fetching contents of directory: {file_content.path}")
                contents.extend(self.repo.get_contents(file_content.path, ref=self.BRANCH_NAME))
            else:
                logging.info(f"File fetched: {file_content.path}")
                files_content.append(file_content)
        return files_content


    def get_hash(self, folder_name: str) -> str:
        
        logging.info(f"Attempting to fetch contents for folder: {folder_name} in repo {self.REPO_NAME} on branch {self.BRANCH_NAME}")
        try:
            contents = self.repo.get_contents(folder_name, ref=self.BRANCH_NAME)
        except UnknownObjectException as e:
            logging.error(f"Failed to fetch folder '{folder_name}'. Error: {e}")
            raise e

        files_content = self.get_files_content(contents)
        logging.info(f"Number of files fetched from folder {folder_name}: {len(files_content)}")
        for file_content in files_content:
            logging.debug(f"File path: {file_content.path}, Content length: {len(file_content.decoded_content) if file_content.type == 'file' else 'N/A'}")
        
        hash_value = str(get_hash_files(files_content))
        logging.info(f"Generated hash for folder {folder_name}: {hash_value}")
        return hash_value


    def get_all_artifacts(self) -> Union[requests.models.Response, Any]:
        url = f"https://api.github.com/repos/{self.REPO_NAME}/actions/artifacts"
        headers = self._get_headers()
        max_retries = 3
        delay = 5
        for attempt in range(max_retries):
            try:
                response = self._request_data(url, headers=headers)
                # logging.info(f"Artifacts response: {response} from {url}")
                if response and response.get("artifacts"):
                    logging.info(f"Artifacts fetched successfully on attempt {attempt+1}")
                    return response
                logging.warning(f"No artifacts found on attempt {attempt+1}/{max_retries}. Retrying in {delay}s...")
                time.sleep(delay)
                return response
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    logging.error(f"No artifacts found for the repository: {self.REPO_NAME}")
                    return None
                else:
                    raise e


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
                self.REPO_NAME,
                GH_ALL_ARTIFACT_ENDPOINT,
                artifact_id,
                archive_format,
            ]
        )
        headers = self._get_headers()
        response = self._request_data(url, headers=headers, dict_format=False)
        logging.info(f"Artifact response: {response}")
        return response


    def _get_headers(self) -> Dict[str, str]:
        self.ACCESS_TOKEN = os.getenv("GH_PAT")

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
    
    
    def get_tests_results_json(self) -> Union[Dict[str, Any], None]:
        response = self.get_all_artifacts()
        if response and response.get("artifacts"):
            # Find the artifact with the test results
            artifact = next((a for a in response["artifacts"] if a["name"] == "tests-results-logs"), None)
            if artifact:
                # Download the artifact content
                artifact_content = self.get_artifact(artifact)
                try:
                    with zipfile.ZipFile(io.BytesIO(artifact_content.content)) as z:
                        with z.open('results.json') as json_file:
                            json_content = json.load(json_file)
                            return json_content
                except Exception as e:
                    logging.error(f"Failed to parse test results JSON from artifact: {e}")
                    return None
        logging.error("No suitable artifacts found or unable to fetch artifact.")
        return None
