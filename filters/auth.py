"""The users' authentication filter."""

from contextvars import ContextVar
from typing import Optional, Union

from aiogram.dispatcher.filters import BoundFilter, FilterNotPassed
from aiogram.types import ChatActions, Message
from aiogram.utils.callback_data import CallbackData

from models import User
from utils.loguru_logging import logger


class AuthFilter(BoundFilter):
    """Check user authentication and create new users if necessary."""

    key = "user"
    required = True

    ctx_user = ContextVar("user_auth")

    def __init__(self, user: Optional[User] = None):
        """Initialize the filter."""
        self.user = user

    async def check(self, *args) -> dict:
        """Check whether the user is authenticated and allowed to use the bot."""
        obj: Union[Message, CallbackData] = args[0]

        try:
            user = self.ctx_user.get()
        except LookupError:
            try:
                user = await User.get(id=obj.from_user.id)
                self.ctx_user.set(user)

            except Exception as e:
                logger.error(f"Exception in {self.__class__.__name__}: {e} ({e.__class__}")
                raise e

        if not user.is_active or user.is_deleted:
            logger.info(
                f'User [ID:{user.pk}] {"is not active" if not user.is_active else "deleted"}'
            )
            logger.debug(f"`obj` is {obj.to_python()}")
            raise FilterNotPassed()

        return {"user": user}
