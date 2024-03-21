import aiogram 
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import __token__
import google_sheet_connect
import json_manager

bot = aiogram.Bot(__token__.TOKEN)
SheetManager = google_sheet_connect.Sheet_Manager()
JsonManager = json_manager.Manager()
admin_chat_ids = SheetManager.get_admins_id()
# print(admin_chat_ids)

'''__________InlineKeyboardButtons__________'''
start_msg_builder = InlineKeyboardBuilder()
inl_btn_order = InlineKeyboardButton(
    text='Створити бронь на лікі 💊', #переделать под доставку
    callback_data='cli_btn_order')
inl_btn_consultation = InlineKeyboardButton(
    text='Задати питання фахівцю 👩‍⚕️', 
    callback_data='cli_btn_consultation')
start_msg_builder.row(inl_btn_order, inl_btn_consultation, width=1)

'''__________ReplyKeyboardButtons__________'''
rpl_btn_geo = KeyboardButton(text="Надати геолокацію🗺", request_location=True)
rpl_btn_contac = KeyboardButton(text="Надати контакт📲", request_contact=True)
kb = [[
    rpl_btn_contac
]]
rpl_builder = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

