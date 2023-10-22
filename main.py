import os
from pathlib import Path

import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from dotenv import load_dotenv

from po_compile import compile_all_languages

load_dotenv()
compile_all_languages()

bot = aiogram.Bot(os.environ["TELEGRAM_BOT_TOKEN"])
storage = MemoryStorage()
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
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_photo = State()


# Handlers
@dp.message_handler(aiogram.filters.CommandStart())
async def start(message: aiogram.types.Message):
    await message.answer(i18n.gettext("bot.start_message", locale=BOT_LANGUAGE))


@dp.message_handler(commands="sell", state="*")
async def enter_sell(message: aiogram.types.Message):
    await SellItem.waiting_for_name.set()
    await message.reply(i18n.gettext("bot.enter_sell_name", locale=BOT_LANGUAGE))


@dp.message_handler(state=SellItem.waiting_for_name, content_types=aiogram.types.ContentTypes.TEXT)
async def enter_name(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await SellItem.waiting_for_price.set()
    await message.reply(i18n.gettext("bot.enter_price", locale=BOT_LANGUAGE))


@dp.message_handler(state=SellItem.waiting_for_price, content_types=aiogram.types.ContentTypes.TEXT)
async def enter_price(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await SellItem.waiting_for_photo.set()
    await message.reply(i18n.gettext("bot.send_photo", locale=BOT_LANGUAGE))


@dp.message_handler(
    state=SellItem.waiting_for_photo, content_types=aiogram.types.ContentTypes.PHOTO
)
async def enter_photo(message: aiogram.types.Message, state: FSMContext):
    photo = message.photo[-1]
    print("here")
    await photo.download(destination_file="item_photo.jpg")

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

    await bot.send_photo(
        "@" + os.environ["CHANNEL_USERNAME"],
        aiogram.types.InputFile("item_photo.jpg"),
        caption=caption,
    )
    await message.reply(i18n.gettext("bot.thanks_sale", locale=BOT_LANGUAGE))


if __name__ == "__main__":
    aiogram.executor.start_polling(dp)
