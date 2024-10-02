from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


async def inline_builder(text: str | list):
    builder = InlineKeyboardBuilder()
    if isinstance(text, str):
        text = [text]

    [builder.button(text=txt) for txt in text]

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_confirm_button_keyboard():
    kbb = InlineKeyboardBuilder()
    kbb.button(text="Добавить кнопку?", callback_data='add_button')
    kbb.button(text="Продолжить без кнопки", callback_data='no_button')
    kbb.adjust(1)
    return kbb.as_markup()
