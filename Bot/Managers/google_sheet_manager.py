import asyncio
import gspread
import aiohttp
from oauth2client.service_account import ServiceAccountCredentials

Scopes = ["https://spreadsheets.google.com/feeds", 
                "https://www.googleapis.com/auth/spreadsheets", 
                "https://www.googleapis.com/auth/drive.file", 
                "https://www.googleapis.com/auth/drive" ]

class Sheet_Manager:
    def __init__(self) -> None:
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name('ejd-notification-bot-59b798978894.json', Scopes)
        self.client = gspread.authorize(self.credentials)
        self.spreadsheet = self.client.open_by_url('https://docs.google.com/spreadsheets/d/120Xq83j6vP2OrKDqLBZz8XYLdW76HH9JXPWphrBH4FM/edit?usp=sharing')

        self.user_auto_sheet = self.spreadsheet.worksheet('admin_users')

    def get_admins_id(self):
        admins = self.user_auto_sheet.get_all_records()
        ids = []
        for adm in admins:
            ids.append(adm['user_id'])
        return ids

    async def _print_data_from_sheet(self):
        print(self.spreadsheet.worksheets())
        print(f'user_auto_sheet ->\n{self.user_auto_sheet.get_all_records()}')
        print(self.user_auto_sheet.get_all_values())

    async def writing_data(self, data):
        user_auto_values = self.user_auto_sheet.get_all_values()
        last_record = len(user_auto_values)

        for row_num, row_data in enumerate(data):
            for col_num, cell_data in enumerate(row_data):
                self.user_auto_sheet.update_cell(row_num + last_record + 1, col_num + 1, cell_data)
        
        print(await self._print_data_from_sheet())

async def main():
    sm = Sheet_Manager()
    # await sm.writing_data()
    await sm._print_data_from_sheet()


if __name__ == "__main__":
    asyncio.run(main())