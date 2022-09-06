from typing import Any, DefaultDict, List

import logging
from collections import defaultdict

import gspread
from github_tests_validator_app.config.config import (
    GSHEET_SA_JSON,
    GSHEET_SPREADSHEET_ID,
    GSHEET_WORKSHEET_CHECK_VALIDATION_REPO,
    GSHEET_WORKSHEET_STUDENT,
    GSHEET_WORKSHEET_STUDENT_CHALLENGE_REF,
    GSHEET_WORKSHEET_STUDENT_CHALLENGE_RESULT,
)
from github_tests_validator_app.lib.pytest_result import PytestResult
from github_tests_validator_app.lib.users import GitHubUser


class GSheet:
    def __init__(self):
        logging.info(f"Connecting to Google Sheet API ...")
        self.gs_client = gspread.service_account(filename=GSHEET_SA_JSON)
        self.spreadsheet = self.gs_client.open_by_key(GSHEET_SPREADSHEET_ID)
        logging.info("Done.")

    def get_new_sheet(self, sheet_id: str) -> gspread.spreadsheet.Spreadsheet:
        self.spreadsheet = self.gs_client.open_by_key(sheet_id)
        return self.spreadsheet

    def add_new_user_on_sheet(self, user: GitHubUser) -> None:
        # Controle the workseet exist of not
        worksheet = self.spreadsheet.worksheet(GSHEET_WORKSHEET_STUDENT)

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

    def add_new_repo_valid_result(self, user: GitHubUser, result: bool, info: str = "") -> None:
        worksheet = self.spreadsheet.worksheet(GSHEET_WORKSHEET_CHECK_VALIDATION_REPO)
        headers = worksheet.row_values(1)
        user_dict = user.__dict__
        new_row = list()
        for header in headers:
            if header == "is_valid":
                new_row.append(str(result))
            elif header == "user_id":
                new_row.append(user.ID)
            elif header == "info":
                new_row.append(info)
            elif header.upper() in user_dict:
                new_row.append(user_dict[header.upper()])
            else:
                new_row.append("")
        worksheet.append_row(new_row)

    def add_new_student_challenge_result(
        self, user: GitHubUser, result: PytestResult, info: str = ""
    ) -> None:
        worksheet = self.spreadsheet.worksheet(GSHEET_WORKSHEET_STUDENT_CHALLENGE_RESULT)
        headers = worksheet.row_values(1)
        user_dict = user.__dict__
        result_dict = result.__dict__
        new_row = list()
        for header in headers:

            if header.upper() in user_dict:
                new_row.append(user_dict[header.upper()])
            elif header.upper() in result_dict:
                new_row.append(result_dict[header.upper()])
            elif header == "info":
                new_row.append(info)
            else:
                new_row.append("")
        worksheet.append_row(new_row)

    def get_challenge_coef(self) -> DefaultDict[str, DefaultDict[str, Any]]:

        worksheet = self.spreadsheet.worksheet(GSHEET_WORKSHEET_STUDENT_CHALLENGE_REF)
        dict_results = defaultdict(
            lambda: defaultdict(list)
        )  # type: DefaultDict[str, DefaultDict[str, Any]]
        for row in worksheet.get_all_records():
            id = row.pop("id")
            breakpoint()
            dict_results[id]["name"].append(row.pop("challenge_name"))
            dict_results[id] = defaultdict(defaultdict, {**dict_results[id], **row})

        return dict_results
