from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

'''__________InlineKeyboardButtons__________'''
adm_order_builder = InlineKeyboardBuilder()
inl_btn_order = InlineKeyboardButton(
    text='Опрацювати', 
    callback_data='adm_process_order')
inl_btn_consultation = InlineKeyboardButton(
    text='Задати питання клієнту', 
    callback_data='adm_consultation')
adm_order_builder.row(inl_btn_order, inl_btn_consultation, width=1)

adm_consultation_builder = InlineKeyboardBuilder()
inl_btn_answer_consultation = InlineKeyboardButton(
    text='Надати відповідь', 
    callback_data='adm_start_chatig')
adm_consultation_builder.row(inl_btn_answer_consultation, width=1)

'''__________ReplyKeyboardButtons__________'''
disconect_consultation = KeyboardButton(text="Завершити поточну комунікацію 🛑")
kb = [[
    disconect_consultation
]]
adm_rpl_builder = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)