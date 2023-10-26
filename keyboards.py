import os
from pathlib import Path

from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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
