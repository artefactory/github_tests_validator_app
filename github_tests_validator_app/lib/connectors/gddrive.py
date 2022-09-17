from typing import Any, Dict, List

import logging
from readline import set_completion_display_matches_hook

from google.auth import default
from googleapiclient.discovery import build


class GoogleDriveConnector:
    def __init__(self):
        logging.info(f"Connecting to Google Drive API ...")
        self.credentials = self._get_credentials()
        self.client = self._get_client()
        logging.info(f"Done.")

    def _get_credentials(self):
        credentials, _ = default(
            scopes=[
                "https://www.googleapis.com/auth/drive",
            ]
        )
        return credentials

    def _get_client(self):
        return build("drive", "v3", credentials=self.credentials)

    def search_folder(self, folder_name: str) -> Any:
        """Get all folders from a google drive.
        ...
        :return: All folders informations.
        :rtype: Any
        """
        results = (
            self.client.files()
            .list(
                q=f"name = '{folder_name}' and (mimeType = 'application/vnd.google-apps.folder')",
                spaces="drive",
                fields="files(id, name, mimeType, permissions)",
            )
            .execute()
        )
        return results.get("files", [])

    def get_all_file(self, file_name: str, parent_folder_ids: str = "") -> Any:
        """Get all files from a folder on Google Drive.
        :param parent_folder_ids: Folder ID.
        ...
        :return: All file informations from a folder.
        :rtype: Any
        """
        query = ""
        if parent_folder_ids:
            query = f"name = '{file_name}'"
        response = (
            self.client.files()
            .list(
                q=query,
                spaces="drive",
                fields="files(id, name, mimeType, permissions)",
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
        folder = self.client.files().create(body=file_metadata).execute()
        logging.info(f'Folder {folder["name"]} has created with ID: "{folder["id"]}".')
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

        batch = self.client.new_batch_http_request(callback=callback)
        user_permission = {"type": "user", "role": "writer", "emailAddress": user_email}
        batch.add(
            self.client.permissions().create(fileId=file_id, body=user_permission, fields="id")
        )
        batch.execute()

        return ids

    def share_file_from_users(self, file_info: Dict[str, Any], users: List[str] = []) -> None:
        if not users:
            return
        user_shared = [user["emailAddress"] for user in file_info.get("permissions", [])]
        new_shared_users = list(set(users) - set(user_shared))
        for user in new_shared_users:
            self.share_file(file_info["id"], user)

    def get_gdrive_folder(self, folder_name: str, shared_user_list: List[str] = []) -> Any:
        """Get the folder information in google drive.
        .. note ::
            If the folder doesn't exist, it will create a new one.
        :param folder_name: Folder title.
        :param user_share: email that we want to share with the folder.
        ...
        :return: informations of the folder
        :rtype: Any
        """
        list_folder = self.search_folder(folder_name)
        for folder in list_folder:
            if folder.get("name", None) == folder_name:
                if shared_user_list:
                    self.share_file_from_users(folder, shared_user_list)
                return folder

        folder = self.create_folder(folder_name)
        if "id" in folder and shared_user_list:
            self.share_file_from_users(folder, shared_user_list)
        return folder

    def get_gsheet(
        self, gsheet_name: str, parent_folder_ids: str = "", shared_user_list: List[str] = []
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
        list_file = self.get_all_file(gsheet_name, parent_folder_ids)
        for file in list_file:
            if file["name"] == gsheet_name and "spreadsheet" in file["mimeType"]:
                if shared_user_list:
                    self.share_file_from_users(file, shared_user_list)
                return file
        file = self.create_google_file(
            gsheet_name,
            "application/vnd.google-apps.spreadsheet",
            [parent_folder_ids],
        )
        if shared_user_list:
            self.share_file_from_users(file, shared_user_list)
        return file

    def create_google_file(
        self, title: str, mimeType: str, parent_folder_ids: List[str] = []
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
        req = self.client.files().create(body=body)
        new_sheet = req.execute()
        return new_sheet
