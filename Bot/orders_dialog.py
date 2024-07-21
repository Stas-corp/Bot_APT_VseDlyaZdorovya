from operator import itemgetter

from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import Dialog, Window, setup_dialogs
from aiogram_dialog.widgets.kbd import (
    CurrentPage, FirstPage, LastPage,
    Multiselect, Select, NextPage, PrevPage,
    Row, ScrollingGroup, Button)
from aiogram_dialog import (
    Dialog, DialogManager)

import __bot_init__ as b_init
import admins_keyboard as adm_kb

bot = b_init.bot
dp = b_init.dp
OrderManager = b_init.OrderManager

class DialogSG(StatesGroup):
    DEFAULT = State()
    PAGERS = State()

async def order_getter(**_kwargs):    
    not_completed_ords = OrderManager.get_NotCompletedOrder()
    processing_ords = await OrderManager.get_orders_in_processing()
    result = []
    for ord in not_completed_ords:
        if ord in processing_ords:
            result.append(f'📍 {ord}')
        else:
            result.append(ord)
    return {'orders': result}

async def reaction(call: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    # processing_ords = await OrderManager.get_orders_in_processing()
    if item_id[0] == '📍':
        await bot.answer_callback_query(call.id, text=f'{item_id} вже ВІДКРИТО!')

    else:
        order = OrderManager.get_order(item_id.split()[-1])
        # print(item_id, call.data)
        await OrderManager.add_order_in_processing(item_id)
        ords = await OrderManager.get_orders_in_processing()
        print(ords)
        await manager.done()
        await dp.fsm.storage.update_data(StorageKey(call.message.bot.id, 
                                                    order['user_id'], 
                                                    order['user_id'],
                                                    destiny='default'),
                                        {'order': order})
        
        admin_message = f"id:{order['user_id']}\n№ Замовлення: {order['order_id']}\nКлієнт: @{order['user_name']}\nІм'я в ТГ: {order['full_name']}\n📍 Адреса: {order['address']}\n📦 Отриманно нове замовлення:\n\n{order['order']}"
        if order['delivery_type'] == 'PK_delivery':
            admin_message += '\n\n❗️❗️❗️Самовивіз❗️❗️❗️'
        elif order['delivery_type'] == 'JK_delivery':
            admin_message += '\n\n❗️❗️❗️Доставка по ЖК❗️❗️❗️'
        await bot.send_contact(chat_id=call.from_user.id,
                                phone_number=order['phone_number'],
                                first_name=order['full_name'])
        await bot.send_message(chat_id=call.from_user.id,
                                text=admin_message, 
                                reply_markup=adm_kb.adm_order_builder.as_markup())
        
        await bot.delete_message(call.message.chat.id,
                                call.message.message_id)
    
dialog = Dialog(
    Window(
        Const("Замовлення які треба опрацювати:"),
        ScrollingGroup(
            Select(
                Format("{item}"),
                items="orders",
                id="adm_get_order",
                # item_id_getter=lambda item: int(item.split()[-1]),
                item_id_getter=lambda item: item,
                on_click=reaction,

            ),
            width=2,
            height=5,
            hide_pager=True,
            id="scroll_no_pager",
        ),
        Row(
            FirstPage(
                scroll="scroll_no_pager", text=Format("⏮️ {target_page1}"),
            ),
            PrevPage(
                scroll="scroll_no_pager", text=Format("◀️"),
            ),
            CurrentPage(
                scroll="scroll_no_pager", text=Format("{current_page1}"),
            ),
            NextPage(
                scroll="scroll_no_pager", text=Format("▶️"),
            ),
            LastPage(
                scroll="scroll_no_pager", text=Format("{target_page1} ⏭️"),
            )
        ),
        getter=order_getter,
        state=DialogSG.PAGERS,
    )
)

dp.include_router(dialog)
setup_dialogs(dp)