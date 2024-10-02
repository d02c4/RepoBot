from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router, Bot
from aiogram import F

from app.filters.rights import IsTeacher
from app.keyboards.fabrics import pagination
from app.keyboards.inline import select_sender, get_select_confirm

from app.models.user import get_source_for_user, get_all_groups, get_users_in_groups, get_unique_courses, \
    get_unique_group_ids_by_courses

router = Router()


class Reg(StatesGroup):
    name = State()
    text = State()
    select_sender = State()
    select_target = State()
    confirm = State()


class Sub(StatesGroup):
    status = State()
    sources = State()


class Teacher(StatesGroup):
    get_data = State()
    get_data_del = State()
    result = State()


@router.message(Command('sub'))
async def sub(message: Message, state: FSMContext):
    await get_source_for_user(message.from_user.id)


@router.message(Command("send"), IsTeacher())
async def reg_one(message: Message, state: FSMContext):
    # Присваиваем состояние пользователю
    mess = await message.answer(text="Введите ваше имя")
    await state.update_data(message=mess)
    await state.set_state(Reg.name)


# ловим состояние фильтром
@router.message(Reg.name)
async def reg_second(message: Message, state: FSMContext):
    mess: Message = (await state.get_data()).get("message")
    # обновили информацию полученную от пользователя
    await state.update_data(name=message.text)
    # Меняем состояние на следующее
    mess = await mess.edit_text(text="Введите текст поста:")
    await state.update_data(message=mess)
    await state.set_state(Reg.text)
    await message.delete()


@router.message(Reg.text)
async def reg_third(message: Message, state: FSMContext):
    mess: Message = (await state.get_data()).get("message")
    await state.update_data(text=message.text)
    # получаем в виде словаря заполненные данные
    await state.set_state(Reg.select_sender)
    await mess.edit_text(text="Выберете цель для рассылки:", reply_markup=select_sender)
    # Очистим состояния
    await message.delete()


@router.callback_query(Reg.select_sender, F.data == 'by_group')
async def reg_3(call: CallbackQuery, state: FSMContext):
    list_all = await get_all_groups()
    for el in list_all:
        el["send"] = False

    await state.update_data(list_all=list_all)
    keyboard = await pagination(0, list_all=list_all, selection="sender_group")
    await call.message.answer('Выбор групп', reply_markup=keyboard)
    await call.answer()
    await call.message.delete()


@router.callback_query(Reg.select_sender, F.data == 'by_course')
async def reg_10(call: CallbackQuery, state: FSMContext):
    tmp_list = await get_unique_courses()
    list_all = []
    for el in tmp_list:
        if el is not None:
            list_all.append({"group_course": el, "send": False})

    await state.update_data(list_all=list_all)
    keyboard = await pagination(0, list_all=list_all, selection="sender_course")
    await call.message.answer('Выбор курсов', reply_markup=keyboard)
    await call.answer()
    await call.message.delete()


@router.callback_query(F.data == 'save_sender1')
async def reg_4(call: CallbackQuery, state: FSMContext):
    await save_sender(call, state, "send_mess1")


@router.callback_query(F.data == 'save_sender2')
async def reg_4(call: CallbackQuery, state: FSMContext):
    await save_sender(call, state, "send_mess2")


async def get_right_len(text: str):
    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            return text[x:x + 4096]
    else:
        return text


async def save_sender(call: CallbackQuery, state: FSMContext, select: str):
    data = await state.get_data()
    list_not_all = []
    for el in data.get("list_all"):
        if el["send"]:
            list_not_all.append(el)
    await state.update_data(list_not_all=list_not_all)
    text = f"Имя:{data['name']}\nСообщение:\n{data['text']}"
    text = await get_right_len(text)
    mess = await call.message.answer(text)
    await state.update_data(message=mess)
    await mess.edit_text(text=mess.text, reply_markup=get_select_confirm(select))
    await state.set_state(Reg.confirm)
    await call.message.delete()


@router.callback_query(Reg.confirm, F.data == 'send_mess1')
async def reg_5(call: CallbackQuery, state: FSMContext):
    # обновили информацию полученную от пользователя
    data = await state.get_data()
    list_not_all = data.get("list_not_all")

    await send_mess(list_not_all, data.get("message"), "group")
    await call.answer(text="Рассылка завершена!")
    await call.message.delete()
    await state.clear()
    await call.answer()


@router.callback_query(Reg.confirm, F.data == 'send_mess2')
async def reg_5(call: CallbackQuery, state: FSMContext):
    # обновили информацию полученную от пользователя
    data = await state.get_data()
    list_not_all = data.get("list_not_all")

    await send_mess(list_not_all, data.get("message"), "course")
    await call.answer(text="Рассылка завершена!")
    await call.message.delete()
    await state.clear()
    await call.answer()


@router.callback_query(Reg.confirm, F.data == 'cancel_mess')
async def reg_6(call: CallbackQuery, state: FSMContext):
    await call.answer(text="Отправка отменена")
    await call.message.delete()
    await state.clear()


async def send_mess(list_not_all, message: Message, select: str = "group"):
    list_ids = []
    if select == "group":
        for el in list_not_all:
            list_ids.append(el["group_id"])
    elif select == "course":
        for el in list_not_all:
            list_ids.append(el["group_course"])
        list_ids = await get_unique_group_ids_by_courses(list_ids)
    list_user = await get_users_in_groups(list_ids)
    for user in list_user:
        try:
            await message.send_copy(user["user_id"], reply_markup=None)
        except Exception as e:
            print(e)
