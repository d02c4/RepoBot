from aiogram.filters import BaseFilter
from aiogram.types import Message

from typing import List

from app.models.user import get_teacher_user_ids, get_admin_user_ids


class IsTeacher(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        teacher_user_ids = await get_teacher_user_ids()
        return message.from_user.id in teacher_user_ids


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        admin_user_ids = await get_admin_user_ids()
        return message.from_user.id in admin_user_ids
