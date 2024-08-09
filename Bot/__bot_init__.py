import logging

import aiogram 
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.loggers import dispatcher

# from aiogram_dialog import setup_dialogs

import __token__
# import orders_dialog
import DB.db_redis as db_redis
import Managers.google_sheet_manager as google_sheet_manager
import Managers.json_manager as json_manager
import Managers.order_manager as order_manager


logger = dispatcher
logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_activity.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

bot = aiogram.Bot(__token__.TOKEN)
dp = aiogram.Dispatcher(storage=db_redis.redis_storage)
# dp.include_router(orders_dialog.dialog)
# setup_dialogs(dp)

SheetManager = google_sheet_manager.Sheet_Manager()
JsonManager = json_manager.UserManager()
OrderManager = order_manager.Manager()
admin_chat_ids = SheetManager.get_admins_id()

apt_adress = {
    'Аптечний пункт №1': [
        'Аптечний пункт №1', 
        'Національний Інститут Раку (хірургічний корпус)', 
        'Київ, вул. Юлії Здановської (Ломоносова) 33/43', 
        '+380635196716', 
        'https://maps.app.goo.gl/ReJezifHAzKCvzkr7'],

    'Аптечний пункт №2': [
        'Аптечний пункт №2', 
        'Броварська багатопрофільна клінічна лікарня (терапевтичний корпус)', 
        'Бровари, вул. Шевченка 14', 
        '+380932446312', 
        'https://maps.app.goo.gl/m8bT95d3BPA2V9yj7'],

    'Аптечний пункт №3': [
        'Аптечний пункт №3', 
        'КНП Бориспільський міський центр первинної медико-санітарної допомоги', 
        'Бориспіль, вул. Леоніда Каденюка (Гагарина) 1', 
        '+380501915634', 
        'https://maps.app.goo.gl/EiCkAUVvdwdqMECx5'],

    'Аптека №3': [
        'Аптека №3', 
        'ЖК Файна Таун, теріторія житлового комплексу', 
        'Київ, вул. Салютна 2 (будинок №22)', 
        '+380635200121', 
        'https://maps.app.goo.gl/MdBKLTgPp7ZEENLdA']
}

def keyboard_apt_adress() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    for apt, info in apt_adress.items():
        # logging.warn(f"cli_apt_address_{apt.replace(' ', '_')}")
        btn = InlineKeyboardButton(
            text=apt,
            callback_data=f"cli_apt_address_{apt.replace(' ', '_')}")
        keyboard.row(btn, width=1)
    return keyboard

def get_apt_info(apt: str) -> str:
    message = ''
    info = apt_adress[apt]
    for str in info:
        message += f'{str}\n'
    return message
        
class Form(StatesGroup):
    no_contact = State()
    view_contats = State()
    order = State()
    order_await = State()
    order_processing = State()
    set_address = State()
    set_full_name = State()
    check_full_name = State()
    save_full_name = State()
    check_address = State()
    save_address = State()
    check_np_address = State()
    save_np_address = State()

    set_pickup_address = State()
    '''preparation for the consultation process'''
    runUp_consultation = State()
    '''consultation process'''
    during_consultation = State()
# print(admin_chat_ids)

# async def set_bot_commands():
#     comands = [BotCommand(command='/start', description='Головне меню'),
#                BotCommand(command='/user', description='Інформація про мене')]
#     await bot.set_my_commands(comands)

'''__________InlineKeyboardButtons__________'''
inl_btn_order_jk = InlineKeyboardButton(
    text='Доставка 💊 по ЖК ',
    callback_data='cli_btn_jkDelivery')
inl_btn_NP_order = InlineKeyboardButton(
    text='Нова Пошта 📦',
    callback_data='cli_btn_NP_order')
inl_btn_pickup_order = InlineKeyboardButton(
    text='Самовивоз 🚶',
    callback_data='cli_btn_pickup_order')
inl_btn_consultation = InlineKeyboardButton(
    text='Задати питання фахівцю 👩‍⚕️', 
    callback_data='cli_btn_consultation')
inl_btn_delivery = InlineKeyboardButton(
    text='Замовити ліки 📦',
    callback_data='cli_btn_order')
inl_btn_save = InlineKeyboardButton(
    text='Зберегти ✅',
    callback_data='cli_btn_save_address')
inl_btn_not_save = InlineKeyboardButton(
    text='Не зберігати ❌',
    callback_data='cli_btn_not_save_address')
inl_accept_yes = InlineKeyboardButton(
    text='Так ✅',
    callback_data='cli_btn_accept_address_yes')
inl_accept_no = InlineKeyboardButton(
    text='Ні ❌',
    callback_data='cli_btn_accept_address_no')
inl_btn_main_menu = InlineKeyboardButton(
    text='Головне меню 📋',
    callback_data='cli_btn_main_menu')

main_menu_bilder = InlineKeyboardBuilder()
main_menu_bilder.row(inl_btn_main_menu, width=1)

start_inl_builder = InlineKeyboardBuilder()
start_inl_builder.row(inl_btn_order_jk, inl_btn_delivery, width=2)
start_inl_builder.row(inl_btn_consultation, width=1)

accept_user_address = InlineKeyboardBuilder()
accept_user_address.row(inl_accept_yes, inl_accept_no, width=2)

menu_delivery_order = InlineKeyboardBuilder()
menu_delivery_order.row(inl_btn_NP_order, inl_btn_pickup_order, width=1)

'''__________ReplyKeyboardButtons__________'''
rpl_btn_geo = KeyboardButton(text="Надати геолокацію🗺", request_location=True)
rpl_btn_contac = KeyboardButton(text="Надати контакт📲", request_contact=True)
kb = [[
    rpl_btn_contac
]]
rpl_builder = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

