import os
from pathlib import Path

from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / "locales"
BOT_LANGUAGE = os.environ.get("BOT_LANGUAGE")

i18n = I18nMiddleware("bot", LOCALES_DIR, default="en")

# Initialize reply keyboard
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
sell_button = KeyboardButton(
    i18n.gettext("bot.start_keyboard_sell", locale=BOT_LANGUAGE)
)  # Create a button with the text "/sell"
help_button = KeyboardButton(i18n.gettext("bot.start_keyboard_help", locale=BOT_LANGUAGE))
start_keyboard.add(sell_button)  # Add the button to the keyboard
start_keyboard.add(help_button)  # Add the button to the keyboard

sell_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_button = KeyboardButton(i18n.gettext("bot.sell_keyboard_cancel", locale=BOT_LANGUAGE))
sell_keyboard.add(cancel_button)

empty_inline_keyboard = InlineKeyboardMarkup()


def moderator_keyboard(userid):
    moderator_inline_keyboard = InlineKeyboardMarkup()
    moderator_inline_keyboard.add(
        InlineKeyboardButton(
            i18n.gettext("bot.moderator_approval", locale=BOT_LANGUAGE),
            callback_data=f"moderator:approved {userid}",
        )
    )
    moderator_inline_keyboard.add(
        InlineKeyboardButton(
            i18n.gettext("bot.moderator_declination", locale=BOT_LANGUAGE),
            callback_data=f"moderator:declined {userid}",
        )
    )
    return moderator_inline_keyboard


def cancel_listing_keyboard(channel_message_id):
    # Cancel listing markup for seller
    reply_markup = InlineKeyboardMarkup()
    reply_markup.add(
        InlineKeyboardButton(
            i18n.gettext("bot.cancel_sell", locale=BOT_LANGUAGE),
            callback_data=f"cancel {channel_message_id}",
        )
    )
    return reply_markup
