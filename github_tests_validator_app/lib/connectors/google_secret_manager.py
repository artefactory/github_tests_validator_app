from typing import Any

from google.cloud import secretmanager


class GSecretManager:
    def __init__(self, project_id: str):
        self.parent = project_id
        self.client = secretmanager.SecretManagerServiceClient()

    def get_access_secret_version(self, secret_name: str, version: str = "1") -> Any:
        name = self.client.secret_version_path(self.parent, secret_name, version)
        response = self.client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload
