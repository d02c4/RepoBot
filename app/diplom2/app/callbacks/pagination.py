from contextlib import suppress

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from app.FSM.FSM_states import Reg

from app.keyboards import fabrics
from app.models.user import (get_source_for_user,
                             get_all_sources,
                             add_user_membership,
                             remove_user_membership,
                             get_groups_student_for_user,
                             get_all_groups_student,
                             add_user_group,
                             remove_user_group)
from app.utils.sender_state import StepsSender

router = Router()


@router.callback_query(fabrics.Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_handler(call: CallbackQuery, callback_data: fabrics.Pagination, state: FSMContext = None):
    list_all = []
    list_not_all = []
    if callback_data.selection == "source":
        list_all = await get_all_sources()
        list_not_all = await get_source_for_user(call.from_user.id)
    elif callback_data.selection == "group":
        list_all = await get_all_groups_student()
        list_not_all = await get_groups_student_for_user(call.from_user.id)
    elif callback_data.selection == "sender_group":
        list_all = (await state.get_data()).get('list_all')
    elif callback_data.selection == "sender_course":
        list_all = (await state.get_data()).get('list_all')

    page_num = int(callback_data.page)
    page = page_num - 1 if page_num > 0 else 0

    if callback_data.action == "next":
        page = page_num + 1 if page_num < (len(list_all) / 6 - 1) else page_num

    with suppress(TelegramBadRequest):
        await call.message.edit_text(
            call.message.text,
            reply_markup=await fabrics.pagination(page, list_all=list_all, list_not_all=list_not_all,
                                                  selection=callback_data.selection)
        )

    await call.answer()


@router.callback_query(fabrics.Pagination.filter(F.action.in_(["save"])))
async def pagination_handler(call: CallbackQuery, state: FSMContext = None):
    with suppress(TelegramBadRequest):
        await call.answer(text="Настройки были сохранены")
        await call.message.delete()

    try:
        if len((await state.get_data()).get('list_all')) > 0:
            await state.set_state(Reg.confirm)
        else:
            pass
    except Exception as e:
        print(e)


@router.callback_query(fabrics.Pagination.filter(F.action.startswith("group_") | F.action.startswith("source_")
                                                 | F.action.startswith("sender_group_")
                                                 | F.action.startswith("sender_course_")))
async def group_callback_handler(call: CallbackQuery, callback_data: fabrics.Pagination, state: FSMContext = None):
    list_all = []
    list_not_all = []

    page_num = int(callback_data.page)
    created = True
    if callback_data.selection == "group":
        el_id = int(callback_data.action.split('_')[1])
        created = await add_user_group(user_id=call.from_user.id, group_id=el_id)
        if not created:
            await remove_user_group(user_id=call.from_user.id, group_id=el_id)
        list_all = await get_all_groups_student()
        list_not_all = await get_groups_student_for_user(call.from_user.id)
    elif callback_data.selection == "source":
        el_id = int(callback_data.action.split('_')[1])
        created = await add_user_membership(user_id=call.from_user.id, source_id=el_id)
        if not created:
            await remove_user_membership(user_id=call.from_user.id, source_id=el_id)
        list_all = await get_all_sources()
        list_not_all = await get_source_for_user(call.from_user.id)
    elif callback_data.selection == "sender_group":
        el_id = int(callback_data.action.split('_')[2])
        list_all = (await state.get_data()).get('list_all')
        for el in list_all:
            if el["group_id"] == el_id:
                el["send"] = not el["send"]
        await state.update_data(list_all=list_all)

    elif callback_data.selection == "sender_course":
        el_id = int(callback_data.action.split('_')[2])
        list_all = (await state.get_data()).get('list_all')
        for el in list_all:
            if el["group_course"] == el_id:
                el["send"] = not el["send"]
        await state.update_data(list_all=list_all)
    with suppress(TelegramBadRequest):
        await call.message.edit_text(
            text=call.message.text,
            reply_markup=await fabrics.pagination(page_num, list_all=list_all, list_not_all=list_not_all,
                                                  selection=callback_data.selection)
        )
    await call.answer()
    # if callback_data.selection == "sender_group" or callback_data.selection == "sender_course":
    #     await state.set_state(StepsSender.q_button)

