from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.consts import TOPICS_COLUMNS
from bot.topics import topics


def build_topics_kb() -> InlineKeyboardMarkup:
    topic_buttons = [InlineKeyboardButton(text=topic.name_topic,
                                          callback_data=topic.data_topic)
                     for topic in topics]

    rows = [list(row) for row in zip(*[iter(topic_buttons)] * TOPICS_COLUMNS)]
    return InlineKeyboardMarkup(inline_keyboard=rows)
