"""The main module of the application."""
import aiogram
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InputFile

from filters.auth import AuthFilter
from middlewares.message_logging_middleware import MessagesLoggingMiddleware
from models import User
from settings import settings
from utils import tortoise_orm
from utils.loguru_logging import logger
from utils.redis_storage import redis_storage

bot = aiogram.Bot(settings.TELEGRAM_BOT_TOKEN)
dp = aiogram.Dispatcher(bot, storage=redis_storage)


# region Filters
dp.bind_filter(
    AuthFilter,
    exclude_event_handlers=[
        dp.errors_handlers,
        dp.poll_handlers,
        dp.poll_answer_handlers,
    ],
)

# endregion


# region Middlewares
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(MessagesLoggingMiddleware())

i18n = aiogram.contrib.middlewares.i18n.I18nMiddleware("messages", default="en")
dp.middleware.setup(i18n)
_ = i18n.gettext
__ = i18n.lazy_gettext

# endregion


# Define states
class SellItem(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_photo = State()


# region Handlers
@dp.message_handler(aiogram.filters.CommandStart())
async def start(message: aiogram.types.Message):
    """`/start` command handler."""
    logger.info(f"Received /start command: {message.text=} from {message.from_user.to_python()=}")
    me = await bot.get_me()
    return await message.answer(
        _("start.welcome", bot_username=me.username, bot_full_name=me.full_name)
    )


@dp.message_handler(commands="sell", state="*")
async def enter_sell(message: aiogram.types.Message):
    await SellItem.waiting_for_name.set()
    await message.reply("Please enter the name of the item you want to sell.")


@dp.message_handler(state=SellItem.waiting_for_name, content_types=aiogram.types.ContentTypes.TEXT)
async def enter_name(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await SellItem.waiting_for_price.set()
    await message.reply("Please enter the price.")


@dp.message_handler(state=SellItem.waiting_for_price, content_types=aiogram.types.ContentTypes.TEXT)
async def enter_price(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await SellItem.waiting_for_photo.set()
    await message.reply("Please send a photo of the item.")


@dp.message_handler(
    state=SellItem.waiting_for_photo, content_types=aiogram.types.ContentTypes.PHOTO
)
async def enter_photo(message: aiogram.types.Message, state: FSMContext):
    photo = message.photo[-1]
    await photo.download("item_photo.jpg")

    # get data and reset state
    user_data = await state.get_data()
    await state.finish()

    # prepare data
    item_name = user_data.get("name")
    item_price = user_data.get("price")
    username = message.from_user.username or message.from_user.id

    caption = f"Item for sale:\n- Name: {item_name}\n- Price: {item_price}\n- Seller: @{username}"

    await bot.send_photo(settings.TELEGRAM_CHANNEL_ID, InputFile("item_photo.jpg"), caption=caption)
    await message.reply("Thank you! Your item is now for sale.")


# endregion


# region Startup and shutdown callbacks
async def on_startup(*_, **__):
    """Startup the bot."""
    me = await bot.get_me()
    logger.info(f"Starting up the https://t.me/{me.username} bot...")

    logger.debug("Initializing the database connection...")
    await tortoise_orm.init()

    # Get or create the first user, which is the bot itself
    me_data = me.to_python()
    await User.get_or_create(id=me_data.pop("id"), defaults=me_data)

    logger.info("Startup complete.")


async def on_shutdown(*_, **__):
    """Shutdown the bot."""
    logger.info("Shutting down...")

    logger.debug("Closing the database connection...")
    await tortoise_orm.shutdown()

    logger.info("Shutdown complete.")


# endregion


if __name__ == "__main__":
    aiogram.executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
