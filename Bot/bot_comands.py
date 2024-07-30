from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram_dialog import DialogManager, StartMode

from __bot_init__ import Form
import __bot_init__ as b_init
from orders_dialog import DialogSG

bot = b_init.bot
dp = b_init.dp
admin_chat_ids = b_init.admin_chat_ids
JsonManager = b_init.JsonManager

async def welcome(user_id, state: FSMContext):
    message = '''Привіт!🖐\nЯ бот🤖 аптеки "Все для Здоров'я".\nДля початку, надайте свій контак, для подальшої комунікації 👇'''
    await state.set_state(Form.no_contact)
    await bot.send_message(user_id,
                            message,
                            reply_markup=b_init.rpl_builder)

async def order_mess(mess: types.Message, user_id: int):
    message = 'Я можу у тебе прийняти бронь на ліки та надати можливисть задати питання фахівцю!'
    await bot.send_message(user_id,
                           message,
                           reply_markup=b_init.start_inl_builder.as_markup())

@dp.message(Command('adm'), F.from_user.id.in_(admin_chat_ids))
async def get_auth_user(mess: types.Message):
    data = JsonManager._get_data_()
    print(data)
    message = ''
    for key, user in data.items():
        print(key)
        print(user)
        message += f'User: @{data[key]["username"]}\nNumber Phone: {data[key]["number"]}\n\n'
    await bot.send_message(mess.from_user.id, message)

@dp.message(Command('user'))
async def user_comand(mess: types.Message, state: FSMContext):
    if JsonManager.login_user(str(mess.from_user.id)):
        data = JsonManager._get_data_()
        message = ''
        for key, value in data[str(mess.from_user.id)].items():
            message += f'{key} - {value}\n'
        await mess.reply(message)
    else:
        await send_welcome(mess, state)

@dp.message(Command('contact'))
async def send_contact(mess: types.Message, state: FSMContext):
    message = 'Наші контакти:'
    await bot.send_message(mess.from_user.id,
                           message)
    
@dp.message(Command('wwww'), F.from_user.id.in_(admin_chat_ids))
async def order_queue(mess: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.PAGERS, mode=StartMode.RESET_STACK)

@dp.message(CommandStart())
async def send_welcome(mess: types.Message, state: FSMContext, dialog_manager: DialogManager):
    if mess.from_user.id in b_init.admin_chat_ids:
        await dialog_manager.start(DialogSG.PAGERS, mode=StartMode.RESET_STACK)
    else:   
        if not JsonManager.login_user(str(mess.from_user.id)):
            message = '''Привіт!🖐\nЯ бот🤖 аптеки "Все для Здоров'я".\nДля початку, надайте свій контак, для подальшої комунікації 👇'''
            await state.set_state(Form.no_contact)
            await bot.send_message(mess.from_user.id,
                                message,
                                reply_markup=b_init.rpl_builder)
        else:
            user_data = await state.get_data()
            if 'order' in user_data and isinstance(user_data['order'], dict):
                # print(user_data)
                order_completed = user_data['order']['order_completed']
                if order_completed:
                    await order_mess(mess, mess.from_user.id)
                else:
                    message = 'У вас є не опрацьоване замовлення! \nДочекайтеся обробки вашого замовлення фахівцем 👩‍⚕️ або зверніться за контактами в описі ☎️'
                    keyboard = InlineKeyboardBuilder().row(b_init.inl_btn_consultation, width=1)
                    await bot.send_message(mess.from_user.id,
                                            message,
                                            reply_markup=keyboard.as_markup())
            else:
                await order_mess(mess, mess.from_user.id)