import re
from typing import Callable, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from config import TOXIC_WORDS_UZ, MAX_MESSAGE_LENGTH
from database import is_banned


TOXIC_PATTERN = re.compile(
    "|".join(re.escape(w) for w in TOXIC_WORDS_UZ),
    re.IGNORECASE,
)


def contains_toxic(text: str) -> bool:
    return bool(TOXIC_PATTERN.search(text))


class ModerationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            if await is_banned(event.from_user.id):
                await event.answer(
                    "⛔ Siz botdan bloklangansiz. Murojaat: @support"
                )
                return
        return await handler(event, data)
