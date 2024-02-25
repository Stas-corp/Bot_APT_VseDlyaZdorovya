import aiogram 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import __token__
import google_sheet_connect

bot = aiogram.Bot(__token__.TOKEN)
SheetManager = google_sheet_connect.Sheet_Manager()
admin_chat_ids = SheetManager.get_admins_id()
# print(admin_chat_ids)

'''__________InlineKeyboardButtons__________'''
btn_authorization = aiogram.types.InlineKeyboardButton(text = 'Authorization', callback_data='authorization')
builder = InlineKeyboardBuilder()
builder.row(btn_authorization)