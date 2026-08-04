"""Track group messages for retrospective moderation cleanup."""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config import config
from services.recent_messages import track_recent_message


class RecentMessagesMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if (
            isinstance(event, Message)
            and event.from_user is not None
            and config.groups.is_main_group(event.chat.id)
        ):
            track_recent_message(event.chat.id, event.from_user.id, event.message_id)
        return await handler(event, data)
