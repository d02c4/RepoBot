from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="Корзина"), KeyboardButton(text="Контакты")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберете пункт меню:'
)