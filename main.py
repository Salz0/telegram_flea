"""The main module of the application."""
import aiogram
from aiogram.contrib.middlewares.logging import LoggingMiddleware

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


# region Handlers
@dp.message_handler(aiogram.filters.CommandStart())
async def start(message: aiogram.types.Message):
    """`/start` command handler."""
    logger.info(f"Received /start command: {message.text=} from {message.from_user.to_python()=}")
    me = await bot.get_me()
    return await message.answer(
        _("start.welcome", bot_username=me.username, bot_full_name=me.full_name),
    )


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
