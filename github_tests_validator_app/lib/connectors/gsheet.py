from typing import Any, Dict, List

import json
import logging

import gspread
from github_tests_validator_app.config.config import GDRIVE_SUMMARY_SPREADSHEET, GSHEET_SA_JSON
from github_tests_validator_app.lib.models.file import GSheetDetailFile, GSheetFile
from github_tests_validator_app.lib.models.pytest_result import PytestResult
from github_tests_validator_app.lib.models.users import GitHubUser


class GSheetConnector:
    def __init__(self, gsheet_summary_file: GSheetFile, gsheet_details_file: GSheetDetailFile):
        self.gsheet_summary_file = gsheet_summary_file
        self.gsheet_details_file = gsheet_details_file

        logging.info(f"Connecting to Google Sheet API ...")
        self.gs_client = gspread.service_account(filename=GSHEET_SA_JSON)
        logging.info("Done.")

        logging.info(f"Init spreadsheet ...")
        self.summary_spreadsheet = self.init_spreadsheet(gsheet_summary_file)
        self.detail_spreadsheet = self.gs_client.open_by_key(gsheet_details_file.ID)
        logging.info(f"Done.")

    def add_worksheet(
        self, spreadsheet: gspread.spreadsheet.Spreadsheet, title: str, headers: List[str]
    ) -> gspread.worksheet.Worksheet:

        new_worksheet = spreadsheet.add_worksheet(title=title, rows=1, cols=1)
        new_worksheet.insert_row(headers)
        return new_worksheet

    def init_spreadsheet(self, gsheet_file: GSheetFile) -> gspread.spreadsheet.Spreadsheet:

        spreadsheet = self.gs_client.open_by_key(gsheet_file.ID)
        all_worksheets = spreadsheet.worksheets()
        all_worksheets_name = [worksheet.title for worksheet in all_worksheets]

        # Init all worksheets
        for worksheet in gsheet_file.WORKSHEETS:

            if worksheet.NAME in all_worksheets_name:
                continue

            if all_worksheets and all_worksheets[0].title == "Sheet1":
                new_worksheet = all_worksheets.pop(0)
                new_worksheet.update_title(worksheet.NAME)
                new_worksheet.insert_row(worksheet.HEADERS)
            else:
                self.add_worksheet(spreadsheet, worksheet.NAME, worksheet.HEADERS)
        return spreadsheet

    def add_new_user_on_sheet(self, user: GitHubUser) -> None:
        # Controle the workseet exist of not
        worksheet = self.summary_spreadsheet.worksheet(
            GDRIVE_SUMMARY_SPREADSHEET["worksheets"]["student"]["name"]
        )

        # Check is user exist
        id_cell = worksheet.find(str(user.ID))
        login_cell = worksheet.find(user.LOGIN)
        if id_cell and login_cell and id_cell.row == login_cell.row:
            logging.info("User already exist in student worksheet.")
        else:
            logging.info(f"Add new user {user.LOGIN} in student worksheet ...")
            headers = worksheet.row_values(1)
            user_dict = user.__dict__
            new_row = [
                user_dict[header.upper()] if header.upper() in user_dict else None
                for header in headers
            ]
            worksheet.append_row(new_row)
            logging.info("Done.")

    def dict_to_row(
        self, headers: List[str], data: Dict[str, Any], to_str: bool = False, **kwargs: Any
    ) -> List[str]:
        result = []
        for header in headers:
            value: Any = ""
            if header in data:
                value = data[header]
            elif header in kwargs:
                value = kwargs[header]
            if to_str and isinstance(value, dict):
                value = json.dumps(value)
            result.append(value)
        return result

    def add_new_repo_valid_result(self, user: GitHubUser, result: bool, info: str = "") -> None:
        worksheet = self.summary_spreadsheet.worksheet(
            GDRIVE_SUMMARY_SPREADSHEET["worksheets"]["check_validation_repo"]["name"]
        )
        headers = worksheet.row_values(1)
        user_dict = {k.lower(): v for k, v in user.__dict__.items()}
        new_row = self.dict_to_row(
            headers, user_dict, to_str=True, info=info, is_valid=str(result), user_id=user.ID
        )
        worksheet.append_row(new_row)

    def add_new_student_result_summary(
        self, user: GitHubUser, result: PytestResult, info: str = ""
    ) -> None:
        worksheet = self.summary_spreadsheet.worksheet(
            GDRIVE_SUMMARY_SPREADSHEET["worksheets"]["student_challenge_results"]["name"]
        )
        headers = worksheet.row_values(1)
        result_dict = {k.lower(): v for k, v in result.__dict__.items()}
        user_dict = {k.lower(): v for k, v in user.__dict__.items()}
        data = {**user_dict, **result_dict}

        new_row = self.dict_to_row(headers, data, to_str=True, info=info)
        worksheet.append_row(new_row)

    def add_new_student_detail_results(
        self, user: GitHubUser, results: List[Dict[str, Any]], workflow_run_id: int
    ) -> None:

        # All worksheets
        list_worksheet = self.detail_spreadsheet.worksheets()
        # Get student worksheet
        student_worksheet = None
        for worksheet in list_worksheet:
            if worksheet.title == user.LOGIN:
                student_worksheet = worksheet
                break

        # Create new worksheet
        if not student_worksheet:
            student_worksheet = self.detail_spreadsheet.add_worksheet(
                title=user.LOGIN, rows=1, cols=1
            )
            student_worksheet.insert_row(self.gsheet_details_file.HEADERS)

        headers = student_worksheet.row_values(1)
        user_dict = {k.lower(): v for k, v in user.__dict__.items()}
        new_rows = []

        for test in results:
            test = {k.lower(): v for k, v in test.items()}
            data = {**user_dict, **test}
            row = self.dict_to_row(headers, data, to_str=True, workflow_run_id=workflow_run_id)
            new_rows.append(row)
        self.detail_spreadsheet.values_append(
            student_worksheet.title, {"valueInputOption": "USER_ENTERED"}, {"values": new_rows}
        )
