import logging

import gspread
from config.config import GSHEET_SA_JSON, GSHEET_WORKSHEET_ID
from lib.user import GitHubUser


class GSheet:
    def __init__(self):
        logging.info(f"Connecting to Google Sheet API ...")
        self.gs_client = gspread.service_account(filename=GSHEET_SA_JSON)
        self.spreadsheet = self.gs_client.open_by_key(GSHEET_WORKSHEET_ID)
        logging.info("Done.")

    def get_new_sheet(self, sheet_id: str) -> gspread.spreadsheet.Spreadsheet:
        self.spreadsheet = self.gs_client.open_by_key(sheet_id)
        return self.spreadsheet

    def add_new_user_on_sheet(self, user: GitHubUser) -> None:
        # Controle the workseet exist of not
        worksheet = self.spreadsheet.worksheet("students")

        # Check is user exist
        id_cell = worksheet.find(user.ID)
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

    def add_new_repo_valid_result(
        self, user: GitHubUser, action: str, result: bool, info: str = ""
    ) -> None:
        worksheet = self.spreadsheet.worksheet("check_validation_repo")
        headers = worksheet.row_values(1)
        user_dict = user.__dict__
        new_row = list()
        for header in headers:
            if header == "is_valid":
                new_row.append(str(result))
            elif header == "action":
                new_row.append(action)
            elif header == "user_id":
                new_row.append(user.ID)
            elif header == "info":
                new_row.append(info)
            elif header.upper() in user_dict:
                new_row.append(user_dict[header.upper()])
            else:
                new_row.append("")
        worksheet.append_row(new_row)
