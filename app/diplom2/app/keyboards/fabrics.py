from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from json import dumps, loads


class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int
    selection: str = ""


async def pagination(page: int = 0, list_all: list = None, list_not_all: list = None, selection: str = ""):
    if list_all is None:
        list_all = []
    if list_not_all is None:
        list_not_all = []
    builder = InlineKeyboardBuilder()
    start_ind = page * 6
    end_ind = min(start_ind + 6, len(list_all))
    for element in list_all[start_ind:end_ind]:
        if selection == "group":
            subscribed = element['group_id'] in [gr['group_id'] for gr in list_not_all]
            text = f"✅ {element['group_name']}" if subscribed else element['group_name']
            builder.add(InlineKeyboardButton(text=text, callback_data=Pagination(action=f"group_{element['group_id']}",
                                                                                 page=page, selection="group").pack()))

        elif selection == "source":
            subscribed = element['source_id'] in [sub['source_id'] for sub in
                                                  list_not_all]
            text = f"✅ {element['source_name']}" if subscribed else element['source_name']
            builder.add(InlineKeyboardButton(text=text, callback_data=Pagination(action=f"source_{element['source_id']}",
                                                                                 page=page, selection=selection).pack()))

        elif selection == "sender_group":
            text = f"✅ {element['group_name']}" if element['send'] else element['group_name']
            builder.add(InlineKeyboardButton(text=text, callback_data=Pagination(
                action=f"sender_group_{element['group_id']}", page=page, selection=selection).pack()))

        elif selection == "sender_course":
            text = f"✅ {element['group_course']}" if element['send'] else element['group_course']
            builder.add(InlineKeyboardButton(text=str(text), callback_data=Pagination(
                action=f"sender_course_{element['group_course']}", page=page, selection=selection).pack()))

    builder.adjust(*3 * [2])
    builder.row(
        InlineKeyboardButton(text='Назад',
                             callback_data=Pagination(action="prev", page=page, selection=selection).pack()),
        InlineKeyboardButton(text='Вперед',
                             callback_data=Pagination(action="next", page=page, selection=selection).pack())

    )
    if selection != "sender_group" and selection != "sender_course":
        builder.row(InlineKeyboardButton(text='Сохранить', callback_data=Pagination(action="save", page=page,
                                                                                    selection=selection).pack()))
    elif selection == "sender_group":
        builder.row(InlineKeyboardButton(text='Сохранить', callback_data="save_sender1"))
    elif selection == "sender_course":
        builder.row(InlineKeyboardButton(text='Сохранить', callback_data="save_sender2"))

    return builder.as_markup(resize=True)
