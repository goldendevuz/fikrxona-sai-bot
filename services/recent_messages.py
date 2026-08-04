"""Short-lived message history used for moderation cleanup."""
import logging
import time
from collections import deque

from aiogram.exceptions import TelegramBadRequest

from config import config

logger = logging.getLogger(__name__)

# (chat_id, user_id) -> deque[(monotonic timestamp, message_id)]
_recent_messages: dict[tuple[int, int], deque[tuple[float, int]]] = {}


def track_recent_message(chat_id: int, user_id: int, message_id: int) -> None:
    """Remember a message long enough for retrospective moderation."""
    key = (chat_id, user_id)
    history = _recent_messages.get(key)
    if history is None:
        history = deque(maxlen=config.nsfw.recent_messages_max)
        _recent_messages[key] = history

    now = time.monotonic()
    cutoff = now - config.nsfw.recent_cleanup_seconds
    while history and history[0][0] < cutoff:
        history.popleft()
    history.append((now, message_id))


async def delete_recent_messages(
    bot, chat_id: int, user_id: int, *, exclude_message_id: int | None = None
) -> int:
    """Delete and forget the user's messages from the configured time window."""
    key = (chat_id, user_id)
    history = _recent_messages.pop(key, None)
    if not history:
        return 0

    cutoff = time.monotonic() - config.nsfw.recent_cleanup_seconds
    message_ids = {
        message_id
        for timestamp, message_id in history
        if timestamp >= cutoff and message_id != exclude_message_id
    }
    if not message_ids:
        return 0

    deleted = 0
    ordered_ids = sorted(message_ids)
    for offset in range(0, len(ordered_ids), 100):
        batch = ordered_ids[offset:offset + 100]
        try:
            await bot.delete_messages(chat_id, batch)
            deleted += len(batch)
        except TelegramBadRequest:
            logger.exception(
                "Failed to batch-delete recent messages for user %s in chat %s",
                user_id, chat_id,
            )
    logger.info(
        "Deleted %s recent messages for user %s in chat %s after NSFW detection",
        deleted, user_id, chat_id,
    )
    return deleted


def clear_recent_messages() -> None:
    """Clear tracked history (primarily for tests)."""
    _recent_messages.clear()
