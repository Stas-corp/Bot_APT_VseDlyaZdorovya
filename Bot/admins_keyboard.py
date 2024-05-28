from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

'''__________InlineKeyboardButtons__________'''
inl_btn_order = InlineKeyboardButton(
    text='Взяти в опрацювання', 
    callback_data='adm_process_order')
inl_btn_qustion_client = InlineKeyboardButton(
    text='Задати питання клієнту', 
    callback_data='adm_consultation')
inl_btn_accept_order = InlineKeyboardButton(
    text='Підтвердити замовлення', 
    callback_data='adm_accept_order')
inl_btn_acept_delivery = InlineKeyboardButton(
    text='Замовлення доставлено',
    callback_data='adm_accept_delivery')
inl_btn_answer_consultation = InlineKeyboardButton(
    text='Надати відповідь', 
    callback_data='adm_start_chatig')
inl_btn_go_to_orders = InlineKeyboardButton(
    text='Перейти до замовлень', 
    callback_data='adm_go_to_orders')

adm_order_builder = InlineKeyboardBuilder()
adm_order_builder.row(inl_btn_order, width=1)

adm_consultation_builder = InlineKeyboardBuilder()
adm_consultation_builder.row(inl_btn_answer_consultation, width=1)

adm_go_to_orders_bilder = InlineKeyboardBuilder()
adm_go_to_orders_bilder.row(inl_btn_go_to_orders, width=1)

'''__________ReplyKeyboardButtons__________'''
disconect_consultation = KeyboardButton(text="Завершити поточну комунікацію 🛑")
kb = [[
    disconect_consultation
]]
adm_rpl_builder = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)