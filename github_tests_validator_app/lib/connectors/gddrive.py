from typing import Any, Dict, List

import json
import logging

from github_tests_validator_app.config.config import GDRIVE_CREDENTIALS_PATH
from google.oauth2 import service_account
from googleapiclient.discovery import Resource, build

SCOPES = ["https://www.googleapis.com/auth/drive"]


class GoogleDriveConnector:
    def __init__(self):

        self.creds_path = GDRIVE_CREDENTIALS_PATH
        self.creds_file = json.load(open(self.creds_path))

        logging.info(f"Connecting to Google Drive API ...")
        self.creds = service_account.Credentials.from_service_account_info(
            self.creds_file, scopes=SCOPES
        )
        self.drive_api = build("drive", "v3", credentials=self.creds)
        logging.info(f"Done.")

    def get_all_folder(self) -> Any:
        """Get all folders from a google drive.
        ...
        :return: All folders informations.
        :rtype: Any
        """
        results = (
            self.drive_api.files()
            .list(q="mimeType = 'application/vnd.google-apps.folder'", spaces="drive")
            .execute()
        )
        return results.get("files", [])

    def get_all_file(self, parent_folder_ids: str = "") -> Any:
        """Get all files from a folder on Google Drive.
        :param parent_folder_ids: Folder ID.
        ...
        :return: All file informations from a folder.
        :rtype: Any
        """
        query = ""
        if parent_folder_ids:
            query = f"parents in '{parent_folder_ids}'"
        response = (
            self.drive_api.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=None,
            )
            .execute()
        )
        return response.get("files", [])

    def create_folder(self, folder_name: str) -> Any:
        """Create a folder in google drive.
        :param folder_name: Folder title.
        ...
        :return: new folder informations
        :rtype: Any
        """
        # create drive api client
        file_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}

        # pylint: disable=maybe-no-member
        folder = self.drive_api.files().create(body=file_metadata, fields="id").execute()
        id = folder.get("id")
        logging.info(f'Folder {folder_name} has created with ID: "{id}".')
        return folder

    def share_file(self, real_file_id: str, user_email: str) -> List[Any]:
        """Share the file with new user email.
        :param real_file_id: File ID.
        :param user_email: email that we want to share with the file.
        ...
        :return: informations of the folder
        :rtype: List[Any]
        """
        ids = []
        file_id = real_file_id

        def callback(request_id, response, exception):
            if exception:
                logging.error(f"Request_Id: {request_id}")
                logging.error(exception)
            else:
                ids.append(response.get("id"))

        batch = self.drive_api.new_batch_http_request(callback=callback)
        user_permission = {"type": "user", "role": "writer", "emailAddress": user_email}
        batch.add(
            self.drive_api.permissions().create(fileId=file_id, body=user_permission, fields="id")
        )
        batch.execute()

        return ids

    def get_gdrive_folder(self, folder_name: str, user_share: str) -> Any:
        """Get the folder information in google drive.
        .. note ::
            If the folder doesn't exist, it will create a new one.
        :param folder_name: Folder title.
        :param user_share: email that we want to share with the folder.
        ...
        :return: informations of the folder
        :rtype: Any
        """
        list_dir = self.get_all_folder()
        for dir in list_dir:
            if dir["name"] == folder_name:
                return dir

        folder = self.create_folder(folder_name)
        if "id" in folder:
            self.share_file(folder["id"], user_share)
        return {
            "name": folder_name,
            "id": folder["id"],
            "kind": "drive#file",
            "mimeType": "application/vnd.google-apps.folder",
        }

    def get_gsheet(
        self, gsheet_name: str, parent_folder_ids: str = "", user_share: str = ""
    ) -> Any:
        """Get the google sheet information.
        .. note ::
            If the google sheet doesn't exist, it will create a new one.
        :param gsheet_name: Google Sheet title.
        :param parent_folder_ids: A list of strings of parent folder ids (if any).
        :param user_share: email that we want to share with the google sheet.
        ...
        :return: informations of the google sheet
        :rtype: Any
        """
        list_file = self.get_all_file(parent_folder_ids)
        for file in list_file:
            if file["name"] == gsheet_name and "spreadsheet" in file["mimeType"]:
                return file
        file = self.create_google_file(
            self.drive_api,
            gsheet_name,
            "application/vnd.google-apps.spreadsheet",
            [parent_folder_ids],
        )
        if user_share:
            self.share_file(file["id"], user_share)
        return file

    def create_google_file(
        self, drive_api: Resource, title: str, mimeType: str, parent_folder_ids: List[str] = []
    ) -> Any:
        """Create a new file on Google drive.
        .. note ::
            Created file is not instantly visible in your Drive search and you need to access it by direct link.
        :param title: File title
        :param parent_folder_ids: A list of strings of parent folder ids (if any).
        ...
        :return: informations of new file
        :rtype: Any
        """
        logging.info(f"Creating Sheet {title}")
        body: Dict[str, Any] = {
            "name": title,
            "mimeType": mimeType,
        }

        if parent_folder_ids:
            body["parents"] = parent_folder_ids

        req = drive_api.files().create(body=body)
        new_sheet = req.execute()

        # Get id of fresh sheet
        return new_sheet
