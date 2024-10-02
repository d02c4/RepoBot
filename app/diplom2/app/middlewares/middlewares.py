from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable


class TestMiddleware(BaseMiddleware):
    # handler - обработчик, сможем запускать в нужный для нас момент
    # event - тип объекта который принимаем (Message, CallbackData)
    # data - дополнительная информация (FSM к примеру)
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        print('Действия до обработчика')

        # обработчик
        result = await handler(event, data)
        print('Действия после обработчика')

        return result
