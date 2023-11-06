import os
from asyncio import gather
from pathlib import Path

import aiogram
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types.callback_query import CallbackQuery
from dotenv import load_dotenv

from models import User, Message
from po_compile import compile_all_languages
from utils import tortoise_orm
from utils.data_validation import validate_photo_as_document
from utils.generalization import create_message_instance
from utils.loguru_logging import logger
from utils.redis_storage import redis_storage

load_dotenv()
compile_all_languages()

from keyboards import (
    start_keyboard,
    sell_keyboard,
    cancel_listing_keyboard,
    moderator_keyboard,
    empty_inline_keyboard,
)

bot = aiogram.Bot(os.environ["TELEGRAM_BOT_TOKEN"])

dp = aiogram.Dispatcher(bot, storage=MemoryStorage())

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / "locales"
BOT_LANGUAGE = os.environ.get("BOT_LANGUAGE")

i18n = I18nMiddleware("bot", LOCALES_DIR, default="en")
dp.middleware.setup(i18n)

if BOT_LANGUAGE not in i18n.locales:
    logger.warning("language is not supported")
    BOT_LANGUAGE = "en"


# Define states
class SellItem(StatesGroup):
    waiting_description = State()
    waiting_for_price = State()
    waiting_for_photo = State()


@dp.message_handler(CommandStart(), state="*")
async def start(message: types.Message):
    user_dict = message.from_user.to_python()
    await User.get_or_create(
        id=message.from_user.id,
        username=user_dict.get("username"),
        first_name=user_dict.get("first_name"),
        last_name=user_dict.get("last_name"),
        is_bot=message.from_user.is_bot,
        phone_number=user_dict.get("phone_number"),
        language_code=message.from_user.language_code,
        start_payload=message.get_args(),
    )
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
    await gather(
        state.finish(),
        create_message_instance(message),
        message.reply(
            i18n.gettext("bot.sell_keyboard_canceled", locale=BOT_LANGUAGE),
            reply_markup=start_keyboard,  # Switch back to the start keyboard
        ),
    )


@dp.message_handler(
    lambda message: message.text == i18n.gettext("bot.start_keyboard_help", locale=BOT_LANGUAGE),
    state="*",
)
async def help_command(message: aiogram.types.Message):
    support_username = os.environ.get("SUPPORT_USERNAME")
    # Assuming `get_or_create_user` is a function that handles User instances.
    help_text = i18n.gettext("bot.help_message", locale=BOT_LANGUAGE).format(
        support_username=support_username
    )
    await gather(
        create_message_instance(message),
        message.reply(help_text, reply_markup=start_keyboard),
    )


@dp.message_handler(
    lambda message: message.text == i18n.gettext("bot.start_keyboard_sell", locale=BOT_LANGUAGE),
    state="*",
)
async def enter_sell(message: aiogram.types.Message):
    await SellItem.waiting_description.set(),
    await gather(
        create_message_instance(message),
        message.reply(
            i18n.gettext("bot.enter_sell_description", locale=BOT_LANGUAGE),
            reply_markup=sell_keyboard,
        ),
    )


@dp.message_handler(
    state=SellItem.waiting_description, content_types=aiogram.types.ContentTypes.TEXT
)
async def enter_name(message: aiogram.types.Message, state: FSMContext):
    await gather(
        state.update_data(name=message.text),
        SellItem.waiting_for_price.set(),
        create_message_instance(
            message=message,
            content_type="description",
        ),
        message.reply(
            i18n.gettext("bot.enter_price", locale=BOT_LANGUAGE), reply_markup=sell_keyboard
        ),
    )


@dp.message_handler(state=SellItem.waiting_for_price, content_types=aiogram.types.ContentTypes.TEXT)
async def enter_price(message: aiogram.types.Message, state: FSMContext):
    await gather(
        state.update_data(price=message.text),
        SellItem.waiting_for_photo.set(),
        create_message_instance(
            message=message,
            content_type="price_or_conditions",
        ),
        message.reply(
            i18n.gettext("bot.send_photo", locale=BOT_LANGUAGE), reply_markup=sell_keyboard
        ),
    )


async def publish_post(message: aiogram.types.Message, state: FSMContext):
    """Publishing a post in the channel and sending a notification to the user"""
    # get data and reset state
    user_data = await state.get_data()

    # prepare data
    item_name = user_data.get("name")
    item_price = user_data.get("price")
    username = message.from_user.username or message.from_user.id
    userid = message.from_user.id

    # Reply keyboard for Moderator
    moderator_inline_keyboard = moderator_keyboard(userid, message.message_id)

    caption = i18n.gettext(
        "bot.item_sale{item_name}-{item_price}-{username}", locale=BOT_LANGUAGE
    ).format(
        item_name=item_name,
        item_price=item_price,
        username=username,
    )

    # Send listing to moderation
    data = await bot.send_photo(
        chat_id=int(os.environ["MODERATOR_CHAT_ID"]),
        photo=aiogram.types.InputFile("item_photo.jpg"),
        caption=caption,
    )
    await gather(
        bot.edit_message_reply_markup(
            chat_id=data.chat.id, message_id=data.message_id, reply_markup=moderator_inline_keyboard
        ),
        state.finish(),
        message.reply(
            i18n.gettext("bot.sent_to_moderation", locale=BOT_LANGUAGE), reply_markup=start_keyboard
        ),
    )


@dp.message_handler(
    state=SellItem.waiting_for_photo, content_types=aiogram.types.ContentTypes.DOCUMENT
)
async def enter_photo_as_document(message: aiogram.types.Message, state: FSMContext):
    # get photo as document
    document = message.document

    # validate photo
    if validate_photo_as_document(document) is False:
        return await message.reply(
            i18n.gettext("bot.invalid_photo_extension", locale=BOT_LANGUAGE),
            reply_markup=sell_keyboard,
        )
    await document.download(destination_file="item_photo.jpg")
    await gather(
        register_publication_into_db("item_photo.jpg", message), publish_post(message, state)
    )


async def register_publication_into_db(destination, message):
    with open(destination, "rb") as file:
        binary_data = file.read()
    await create_message_instance(message=message, content=binary_data, status="pending")


@dp.message_handler(
    state=SellItem.waiting_for_photo, content_types=aiogram.types.ContentTypes.PHOTO
)
async def enter_photo(message: aiogram.types.Message, state: FSMContext):
    # get photo
    photo = message.photo[-1]
    await photo.download(destination_file="item_photo.jpg")
    await register_publication_into_db("item_photo.jpg", message)
    await gather(publish_post(message, state))


@dp.callback_query_handler(lambda query: query.data[:7] == "cancel ")
async def cancel_sell(query: CallbackQuery):
    data = query.data
    if not data or len(data.split("cancel ")) != 2:
        return await query.answer(i18n.gettext("bot.error"))
    channel_msg_id, msg_id = data.lstrip("cancel ").split(".")
    try:
        await bot.delete_message(f"@{os.environ['CHANNEL_USERNAME']}", channel_msg_id)
    except aiogram.utils.exceptions.MessageToDeleteNotFound:
        return await query.answer(i18n.gettext("bot.error"))
    await gather(
        Message.filter(message_id=msg_id, from_user_id=query.from_user.id).update(
            status="delisted"  # noqa
        ),
        query.answer(i18n.gettext("bot.deleted_successfully")),
        bot.send_message(
            chat_id=query.from_user.id,
            text=i18n.gettext("bot.sell_keyboard_canceled", locale=BOT_LANGUAGE),
        ),
        bot.edit_message_reply_markup(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=empty_inline_keyboard,
        ),
    )


@dp.callback_query_handler(lambda query: query.data[:10] == "moderator:")
async def moderator_callback(query: CallbackQuery):
    callback_data = query.data
    if len(callback_data.split(" ")) != 2:
        await query.answer(i18n.gettext("bot.error"))
        return
    moderator_response = callback_data.split(" ")[0]
    seller_userid, msg_id = callback_data.split(" ")[-1].split(".")
    seller_userid = int(seller_userid)
    match moderator_response:
        case "moderator:approved":
            status = "approved"
            # Get item photo
            photo = query.message.photo[-1]
            await gather(
                query.answer(i18n.gettext("bot.approved_successfully")),
                photo.download(destination_file="item_photo.jpg"),
            )
            # Send item to channel
            data = await bot.send_photo(
                "@" + os.environ["CHANNEL_USERNAME"],
                aiogram.types.InputFile("item_photo.jpg"),
                caption=query.message.caption,
            )
            reply_markup = cancel_listing_keyboard(data.message_id, msg_id)

            await gather(
                # Sending item to the user
                bot.send_photo(
                    chat_id=seller_userid,
                    photo=types.InputFile("item_photo.jpg"),
                    caption=i18n.gettext(
                        "bot.listing_approved{listing}", locale=BOT_LANGUAGE
                    ).format(listing=query.message.caption),
                    reply_markup=reply_markup,
                ),
                # Remove the reply keyboard for moderator
                bot.edit_message_reply_markup(
                    chat_id=query.message.chat.id,
                    message_id=query.message.message_id,
                    reply_markup=empty_inline_keyboard,
                ),
            )
        case "moderator:declined":
            status = "declined"
            await gather(
                query.answer(i18n.gettext("bot.declined_successfully")),
                # Notify user that listing was declined
                bot.send_photo(
                    chat_id=seller_userid,
                    photo=types.InputFile("item_photo.jpg"),
                    caption=i18n.gettext(
                        "bot.listing_declined{listing}", locale=BOT_LANGUAGE
                    ).format(listing=query.message.caption),
                ),
                # Remove the reply keyboard for moderator
                bot.edit_message_reply_markup(
                    chat_id=query.message.chat.id,
                    message_id=query.message.message_id,
                    reply_markup=empty_inline_keyboard,
                ),
            )
        case _:
            status = "moderation error"
            logger.info(f"'{moderator_response=}'")
            await query.answer(i18n.gettext("bot.error"))
    await Message.filter(message_id=msg_id, from_user_id=query.from_user.id).update(status=status)


async def on_startup(*_, **__):
    me = await bot.get_me()
    logger.info(f"Starting up the https://t.me/{me.username} bot...")
    if os.environ.get("DATABASE_URL") != "":
        logger.info("Initializing the database connection...")
        await tortoise_orm.init()
        me_data = me.to_python()
        # logger.debug(me_data)
        await User.get_or_create(id=me_data.pop("id"), defaults=me_data)

    logger.success("Bot started")


async def on_shutdown(*_, **__):
    logger.info("Shutting down...")

    if os.environ.get("DATABASE_URL") != "":
        logger.info("Closing the database connection...")
        await tortoise_orm.shutdown()

    logger.success("Bot shutdown")


if __name__ == "__main__":
    aiogram.executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
