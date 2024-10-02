from typing import Callable, Awaitable, Any

from app.models.user import User
from aiogram import BaseMiddleware
from aiogram.types import Update


class UserMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
                       event: Update,
                       data: dict[str, Any]) -> None:
        current_event = (
                event.message
                or event.callback_query
                or event.inline_query
                or event.chosen_inline_result
        )

        user = await User.create(
            id=current_event.from_user.id,
            username=current_event.from_user.username
        )

        data["user"] = user[0]
        return await handler(event, data)
