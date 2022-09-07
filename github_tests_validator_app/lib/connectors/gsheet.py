from typing import Any, Dict, List

import json
import logging

import gspread
from github_tests_validator_app.config.config import (
    GSHEET_DETAILS_SPREADSHEET_ID,
    GSHEET_HEADER_DETAILS_SPREADSHEET,
    GSHEET_SA_JSON,
    GSHEET_SUMMARY_SPREADSHEET_ID,
    GSHEET_WORKSHEET_CHECK_VALIDATION_REPO,
    GSHEET_WORKSHEET_STUDENT,
    GSHEET_WORKSHEET_STUDENT_CHALLENGE_RESULT,
)
from github_tests_validator_app.lib.pytest_result import PytestResult
from github_tests_validator_app.lib.users import GitHubUser


class GSheetConnector:
    def __init__(self):
        logging.info(f"Connecting to Google Sheet API ...")
        self.gs_client = gspread.service_account(filename=GSHEET_SA_JSON)
        self.summary_spreadsheet = self.gs_client.open_by_key(GSHEET_SUMMARY_SPREADSHEET_ID)
        self.detail_spreadsheet = self.gs_client.open_by_key(GSHEET_DETAILS_SPREADSHEET_ID)
        logging.info("Done.")

    def add_new_user_on_sheet(self, user: GitHubUser) -> None:
        # Controle the workseet exist of not
        worksheet = self.summary_spreadsheet.worksheet(GSHEET_WORKSHEET_STUDENT)

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
        worksheet = self.summary_spreadsheet.worksheet(GSHEET_WORKSHEET_CHECK_VALIDATION_REPO)
        headers = worksheet.row_values(1)
        user_dict = {k.lower(): v for k, v in user.__dict__.items()}
        new_row = self.dict_to_row(
            headers, user_dict, to_str=True, info=info, is_valid=str(result), user_id=user.ID
        )
        worksheet.append_row(new_row)

    def add_new_student_result_summary(
        self, user: GitHubUser, result: PytestResult, info: str = ""
    ) -> None:
        worksheet = self.summary_spreadsheet.worksheet(GSHEET_WORKSHEET_STUDENT_CHALLENGE_RESULT)
        headers = worksheet.row_values(1)
        user_dict = user.__dict__
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
            student_worksheet.insert_row(GSHEET_HEADER_DETAILS_SPREADSHEET)

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
