import asyncio
import aiogram 
from aiogram.types import KeyboardButton, InlineKeyboardButton, BotCommand
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup

import __token__
import Managers.google_sheet_manager as google_sheet_manager
import Managers.json_manager as json_manager
import Managers.order_manager as order_manager

bot = aiogram.Bot(__token__.TOKEN)
dp = aiogram.Dispatcher()
SheetManager = google_sheet_manager.Sheet_Manager()
JsonManager = json_manager.Manager()
OrderManager = order_manager.Manager()
admin_chat_ids = SheetManager.get_admins_id()

class Form(StatesGroup):
    no_contact = State()
    order = State()
    order_await = State()
    order_processing = State()
    set_adress = State()
    set_full_name = State()
    check_full_name = State()
    save_full_name = State()
    check_adress = State()
    save_adress = State()
    check_np_adress = State()
    save_np_adress = State()
    runUp_consultation = State()
    '''preparation for the consultation process'''
    during_consultation = State()
    '''consultation process'''
# print(admin_chat_ids)

# async def set_bot_commands():
#     comands = [BotCommand(command='/start', description='Головне меню'),
#                BotCommand(command='/user', description='Інформація про мене')]
#     await bot.set_my_commands(comands)

'''__________InlineKeyboardButtons__________'''
inl_btn_order = InlineKeyboardButton(
    text='Доставка 💊 по ЖК ',
    callback_data='cli_btn_jkDelivery')
inl_btn_consultation = InlineKeyboardButton(
    text='Задати питання фахівцю 👩‍⚕️', 
    callback_data='cli_btn_consultation')
inl_btn_delivery = InlineKeyboardButton(
    text='Замовити лікі 📦',
    callback_data='cli_btn_order')
inl_btn_save = InlineKeyboardButton(
    text='Зберегти ✅',
    callback_data='cli_btn_save_adress')
inl_btn_not_save = InlineKeyboardButton(
    text='Не зберігати ❌',
    callback_data='cli_btn_not_save_adress')
inl_accept_yes = InlineKeyboardButton(
    text='Так ✅',
    callback_data='cli_btn_accept_adress_yes')
inl_accept_no = InlineKeyboardButton(
    text='Ні ❌',
    callback_data='cli_btn_accept_adress_no')
inl_btn_NP_order = InlineKeyboardButton(
    text='Нова Пошта 📦',
    callback_data='cli_btn_NP_order')
inl_btn_pickup_order = InlineKeyboardButton(
    text='Самовивоз',
    callback_data='cli_btn_pickup_order')


start_inl_builder = InlineKeyboardBuilder()
start_inl_builder.row(inl_btn_order, inl_btn_delivery, width=2)
start_inl_builder.row(inl_btn_consultation, width=1)

accept_user_adress = InlineKeyboardBuilder()
accept_user_adress.row(inl_accept_yes, inl_accept_no, width=2)

menu_delivery_order = InlineKeyboardBuilder()
menu_delivery_order.row(inl_btn_NP_order, inl_btn_pickup_order, width=1)

'''__________ReplyKeyboardButtons__________'''
rpl_btn_geo = KeyboardButton(text="Надати геолокацію🗺", request_location=True)
rpl_btn_contac = KeyboardButton(text="Надати контакт📲", request_contact=True)
kb = [[
    rpl_btn_contac
]]
rpl_builder = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

