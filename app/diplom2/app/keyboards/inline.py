from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup
)

select_sender = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="По группам", callback_data="by_group"
            ),
            InlineKeyboardButton(
                text="По курсам", callback_data="by_course"
            )
        ]
    ]
)


def get_select_confirm(com: str):
    select_confirm = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Разослать", callback_data=str(com)
                ),
                InlineKeyboardButton(
                    text="Отменить", callback_data="cancel_mess"
                )
            ]
        ]
    )
    return select_confirm
