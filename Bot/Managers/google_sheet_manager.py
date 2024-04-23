import asyncio
import gspread
import aiohttp
from gspread import Worksheet
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
        self.np_delivery_sheet = self.spreadsheet.worksheet('NP_Delivery')
        self.salutna_delivery_sheet = self.spreadsheet.worksheet('Salutna_Delivery')

    def get_admins_id(self):
        admins = self.user_auto_sheet.get_all_records()
        ids = []
        for adm in admins:
            ids.append(adm['user_id'])
        return ids

    async def _print_data_from_sheet(self, table: Worksheet):
        print(self.spreadsheet.worksheets())
        print(f'user_auto_sheet ->\n{table.get_all_records()}')
        print(table.get_all_values())

    async def writing_data(self, table: Worksheet, data: list[str]):
        user_auto_values = table.get_all_values()
        last_record = len(user_auto_values)

        for col_num, row_data in enumerate(data):
            for row_num, cell_data in enumerate(row_data):
                table.update_cell(row_num + last_record + 1, col_num + 1, cell_data)
        
        # print(await self._print_data_from_sheet(table))

    async def writing_order(self, sheet: Worksheet, user_id: str, user_name: str, phone_number: str, full_name: str, order: str, address: str):
        data = [user_id, user_name, phone_number, full_name, order, address]
        user_auto_values = sheet.get_all_values()
        last_record = len(user_auto_values)

        for i, cell_data in enumerate(data):
            sheet.update_cell(last_record + 1, i + 1, cell_data)

        # await self._print_data_from_sheet(self.np_delivery_sheet)

async def main():
    sm = Sheet_Manager()
    await sm.writing_order('1123','11333','1132','1123','1123','11323')
    # await sm.writing_data(sm.np_delivery_sheet, ['1','1','1','1','1','1'])
    # await sm._print_data_from_sheet(sm.np_delivery_sheet)
    # for index, item in enumerate(['1123','11333','1132','1123','1123','11323']):
    #     print(f"Индекс: {index}, Элемент: {item}")

if __name__ == "__main__":
    asyncio.run(main())