from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

'''__________InlineKeyboardButtons__________'''
order_adm_builder = InlineKeyboardBuilder()
inl_btn_order = InlineKeyboardButton(
    text='Опрацювати', 
    callback_data='process_order')
inl_btn_consultation = InlineKeyboardButton(
    text='Задати питання клієнту', 
    callback_data='adm_consultation')
order_adm_builder.row(inl_btn_order, inl_btn_consultation, width=1)