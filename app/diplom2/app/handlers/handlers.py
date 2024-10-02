import re

from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Contact
import app.keyboards.inline as kb_inline
from app.FSM.FSM_states import Teacher
from app.filters.rights import IsAdmin
from app.models.user import add_user, get_source_for_user, add_vk_source, delete_vk_source, add_teacher_to_group, \
    remove_teacher_from_all_groups, delete_user
from app.keyboards.fabrics import pagination, Pagination
from app.models.user import (get_source_for_user,
                             get_all_sources,
                             get_all_groups_student,
                             get_groups_student_for_user)
from app.utils import vk

router = Router()


# Миддлваре работает только на сообщения
# router.message.middleware(TestMiddleware())


# router.message.outer_middleware(TestMiddleware())

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username
    if username is None:
        username = ""

    result = await add_user(user_id, username)

    if result:
        await message.answer("Вы были успешно добавлены в базу данных")
    else:
        await message.answer("Ваша персона уже добавлена в базу")


@router.message(Command('delete'))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    try:
        res = await delete_user(message.from_user.id)
        if res == 1:
            await message.answer(text="Ваши данные были успешно удалены из БД")
        else:
            await message.answer(text="Ваших данных уже нет в БД")
    except Exception:
        await message.answer(text="Ваших данных уже нет в БД")


@router.message(Command('sub'))
async def cmd_sub(message: Message):
    all_sources = await get_all_sources()
    subs = await get_source_for_user(message.from_user.id)
    keyboard = await pagination(0, list_all=all_sources, list_not_all=subs, selection="source")
    await message.answer('Выберете источники:', reply_markup=keyboard)


@router.message(Command('register'))
async def cmd_sub(message: Message):
    all_group = await get_all_groups_student()
    user_group = await get_groups_student_for_user(message.from_user.id)
    keyboard = await pagination(0, list_all=all_group, list_not_all=user_group, selection="group")
    await message.answer('Выберете группу:', reply_markup=keyboard)


@router.message(Command('add_vk'), IsAdmin())
async def add_vk(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.answer(text="Для добавления источника вк нужно ввести /add_vk и ссылки на группу через пробел")
        return
    try:
        s = command.args.split(' ')
        text = ''
        for el in s:
            if vk.is_vk_group_link(el):
                wow = vk.return_info_vk_group(el)
                res = await add_vk_source(wow)
                if res == 1:
                    text += f'Источник {wow[3]} успешно добавлен!\n\n'
                else:
                    text += f'Источник {el} не добавлен!\n\n'
            else:
                text += f'Источник {el} не является ссылкой на группу!\n\n'
        await message.answer(text=text)
    except TypeError:
        await message.answer("Произошла ошибка добавления")


@router.message(Command('del_vk'), IsAdmin())
async def del_vk(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.answer(text="Для удаления источника вк нужно ввести /del_vk и ссылку на группу")
        return
    try:
        s = command.args.split(' ')
        text = ''
        for el in s:
            if vk.is_vk_group_link(el):
                wow = vk.return_info_vk_group(el)
                res = await delete_vk_source(wow[1])
                if res == 1:
                    text += f'Источник {wow[3]} успешно удален!\n\n'
                else:
                    text += f'Источник {el} не удален!\n\n'
            else:
                text += f'Источник {el} не является ссылкой на группу!\n\n'
        await message.answer(text=text)
    except TypeError:
        await message.answer("Источника нет в базе")


@router.message(Command('add_teacher'), IsAdmin())
async def cmd_add_teacher(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    mess = await message.answer(text="Отправьте контакт пользователя!")
    await state.update_data(message=mess)
    await state.set_state(Teacher.get_data)


@router.message(Command('del_teacher'), IsAdmin())
async def cmd_add_teacher(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    mess = await message.answer(text="Отправьте контакт пользователя!")
    await state.update_data(message=mess)
    await state.set_state(Teacher.get_data_del)


# ловим состояние фильтром
@router.message(Teacher.get_data)
async def reg_second(message: Message, state: FSMContext):
    try:
        if message.contact is not None:
            user_id = message.contact.user_id
            res = await add_teacher_to_group(user_id)
            if res == 1:
                data = await state.get_data()
                mess: Message = data.get("message")
                await mess.delete()
                await message.answer(text="Пользователь успешно повышен до преподавателя")
                await state.clear()

            else:
                await message.answer(text="Пользователя нет в базе данных, либо он уже преподаватель, отправьте другого")
                await state.set_state(Teacher.get_data)
        else:
            await message.answer("Отправьте контакт пользователя!\n")
            await state.set_state(Teacher.get_data)
    except:
        await message.answer("Отправьте контакт пользователя!\n")
        await state.set_state(Teacher.get_data)
    await message.delete()


# ловим состояние фильтром
@router.message(Teacher.get_data_del)
async def reg_second(message: Message, state: FSMContext):
    try:
        if message.contact is not None:
            user_id = message.contact.user_id
            res = await remove_teacher_from_all_groups(user_id)
            if res == 1:
                data = await state.get_data()
                mess: Message = data.get("message")
                await mess.delete()
                await message.answer(text="Пользователь успешно разжалован из преподавателей")
                await state.clear()
            else:
                await message.answer(text="Пользователя нет в базе данных")
                await state.set_state(Teacher.get_data_del)
        else:
            await message.answer("Отправьте контакт пользователя!\n")
            await state.set_state(Teacher.get_data_del)
    except:
        await message.answer("Отправьте контакт пользователя!\n")
        await state.set_state(Teacher.get_data_del)
    await message.delete()

# @router.message(F.photo)
# async def get_photo(message: Message):
#     await message.answer(text=f"id:= {message.photo[-1].file_id}")
