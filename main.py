import asyncio
import os
from pathlib import Path

import aiogram
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.callback_query import CallbackQuery
from dotenv import load_dotenv

from po_compile import compile_all_languages

from utils import tortoise_orm
from models import User
from utils.loguru_logging import logger

load_dotenv()
compile_all_languages()

from keyboards import start_keyboard, sell_keyboard

bot = aiogram.Bot(os.environ["TELEGRAM_BOT_TOKEN"])

# Redis parameters initialisation
redis_url = os.environ["REDIS_URL"]
redis_port = int(os.environ["REDIS_PORT"])
redis_db = int(os.environ["REDIS_DB"])
redis_pool_size = int(os.environ["REDIS_POOL_SIZE"])
redis_prefix_key = os.environ["REDIS_PREFIX_KEY"]

storage = RedisStorage2(
    redis_url, redis_port, db=redis_db, pool_size=redis_pool_size, prefix=redis_prefix_key
)

dp = aiogram.Dispatcher(bot, storage=storage)

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / "locales"
BOT_LANGUAGE = os.environ.get("BOT_LANGUAGE")

i18n = I18nMiddleware("bot", LOCALES_DIR, default="en")
dp.middleware.setup(i18n)

if BOT_LANGUAGE not in i18n.locales:
    print("language is not supported")
    BOT_LANGUAGE = "en"


# Define states
class SellItem(StatesGroup):
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_photo = State()


@dp.message_handler(CommandStart(), state="*")
async def start(message: types.Message):
    await message.answer(
        i18n.gettext("bot.start_message", locale=BOT_LANGUAGE),
        reply_markup=start_keyboard,  # Attach the reply keyboard here
    )


@dp.message_handler(
    lambda message: message.text.lower()
    == i18n.gettext("bot.sell_keyboard_cancel", locale=BOT_LANGUAGE).lower(),
    state="*",
)
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply(
        i18n.gettext("bot.sell_keyboard_canceled", locale=BOT_LANGUAGE),
        reply_markup=start_keyboard,  # Switch back to the start keyboard
    )


@dp.message_handler(
    lambda message: message.text == i18n.gettext("bot.start_keyboard_help", locale=BOT_LANGUAGE),
    state="*",
)
async def help_command(message: aiogram.types.Message):
    support_username = os.environ.get("SUPPORT_USERNAME")
    help_text = i18n.gettext("bot.help_message", locale=BOT_LANGUAGE).format(
        support_username=support_username
    )
    await message.reply(help_text, reply_markup=start_keyboard)


@dp.message_handler(
    lambda message: message.text == i18n.gettext("bot.start_keyboard_sell", locale=BOT_LANGUAGE),
    state="*",
)
async def enter_sell(message: aiogram.types.Message):
    await SellItem.waiting_for_description.set()
    await message.reply(
        i18n.gettext("bot.enter_sell_description", locale=BOT_LANGUAGE), reply_markup=sell_keyboard
    )


@dp.message_handler(
    state=SellItem.waiting_for_description, content_types=aiogram.types.ContentTypes.TEXT
)
async def enter_name(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await SellItem.waiting_for_price.set()
    await message.reply(
        i18n.gettext("bot.enter_price", locale=BOT_LANGUAGE), reply_markup=sell_keyboard
    )


@dp.message_handler(state=SellItem.waiting_for_price, content_types=aiogram.types.ContentTypes.TEXT)
async def enter_price(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await SellItem.waiting_for_photo.set()
    await message.reply(
        i18n.gettext("bot.send_photo", locale=BOT_LANGUAGE), reply_markup=sell_keyboard
    )


async def publish_post(message: aiogram.types.Message, state: FSMContext):
    """Publishing a post in the channel and sending a notification to the user"""
    # get data and reset state
    user_data = await state.get_data()
    await state.finish()

    # prepare data
    item_name = user_data.get("name")
    item_price = user_data.get("price")
    username = message.from_user.username or message.from_user.id

    caption = i18n.gettext(
        "bot.item_sale{item_name}-{item_price}-{username}", locale=BOT_LANGUAGE
    ).format(
        item_name=item_name,
        item_price=item_price,
        username=username,
    )

    data = await bot.send_photo(
        "@" + os.environ["CHANNEL_USERNAME"],
        aiogram.types.InputFile("item_photo.jpg"),
        caption=caption,
    )
    reply_markup = InlineKeyboardMarkup()
    reply_markup.add(
        InlineKeyboardButton(
            i18n.gettext("bot.cancel_sell", locale=BOT_LANGUAGE),
            callback_data=f"cancel {data.message_id}",
        )
    )
    # Sending photo to the user
    data_user = await bot.send_photo(
        chat_id=message.from_user.id,
        photo=types.InputFile("item_photo.jpg"),
        caption=caption,
    )

    # Edit the message to the user to add the reply markup
    await bot.edit_message_reply_markup(
        chat_id=message.from_user.id,
        message_id=data_user.message_id,
        reply_markup=reply_markup,
    )
    await message.reply(
        i18n.gettext("bot.thanks_sale", locale=BOT_LANGUAGE), reply_markup=start_keyboard
    )


@dp.message_handler(
    state=SellItem.waiting_for_photo, content_types=aiogram.types.ContentTypes.DOCUMENT
)
async def enter_photo_as_document(message: aiogram.types.Message, state: FSMContext):
    # get photo as document
    document = message.document
    await document.download(destination_file="item_photo.jpg")

    # publishing a post
    await publish_post(message, state)


@dp.message_handler(
    state=SellItem.waiting_for_photo, content_types=aiogram.types.ContentTypes.PHOTO
)
async def enter_photo(message: aiogram.types.Message, state: FSMContext):
    # get photo
    photo = message.photo[-1]
    print("here")
    await photo.download(destination_file="item_photo.jpg")

    # publishing a post
    await publish_post(message, state)


@dp.callback_query_handler()
async def cancel_sell(query: CallbackQuery):
    data = query.data
    if not data or len(data.split("cancel ")) != 2:
        await query.answer(i18n.gettext("bot.error"))
        return
    message_id = int(data.split("cancel ")[1])
    try:
        await bot.delete_message(f"@{os.environ['CHANNEL_USERNAME']}", message_id)
    except aiogram.utils.exceptions.MessageToDeleteNotFound:
        await query.answer(i18n.gettext("bot.error"))
        return
    # Answer the query first
    await query.answer(i18n.gettext("bot.deleted_successfully"))
    # Then send the message
    await bot.send_message(
        chat_id=query.from_user.id,
        text=i18n.gettext("bot.sell_keyboard_canceled", locale=BOT_LANGUAGE),
    )


async def on_startup(*_, **__):
    me = await bot.get_me()
    logger.info(f"Starting up the https://t.me/{me.username} bot...")

    logger.info("Initializing the database connection...")
    await tortoise_orm.init()

    me_data = me.to_python()
    await User.get_or_create(id=me_data.pop("id"), defaults=me_data)

    logger.success("Bot started")


async def on_shutdown(*_, **__):
    logger.info("Shutting down...")

    logger.info("Closing the database connection...")
    await tortoise_orm.shutdown()

    logger.success("Bot shutdown")


if __name__ == "__main__":
    aiogram.executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
