"""The middleware to log all the incoming messages into the database."""

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from arrow import arrow

from models import Message, User
from utils.loguru_logging import logger


class MessagesLoggingMiddleware(BaseMiddleware):
    """The middleware class, inherited from `BaseMiddleware`."""

    @staticmethod
    async def _save_message(msg: types.Message) -> Message:
        """Save the message into the database."""
        if msg.reply_to_message:
            reply_to_message = await Message.get_or_none(
                message_id=msg.reply_to_message.message_id,
                chat_id=msg.chat.id,  # `message_id` is not unique. For details, see `models.py`.
            )
        else:
            reply_to_message = None

        return await Message.create(
            # Primary fields
            message_id=msg.message_id,
            from_user_id=msg.from_user.id,
            chat_id=msg.chat.id,
            text=msg.text,
            date=msg.date,
            # Other fields that might be useful
            reply_to_message=reply_to_message,
            content_type=msg.content_type,
            complete_message_json=msg.as_json(),
        )

    async def on_pre_process_message(self, msg: types.Message, *_, **__):
        """Save the message into the database _before_ processing it."""
        user_data: dict = msg.from_user.to_python()
        try:
            # Create a user first, if not exist. Otherwise, we are unable to create a message
            # with a foreign key.
            user, created = await User.get_or_create(id=user_data.pop("id"), defaults=user_data)

            if created:
                if payload := msg.get_args():
                    user.start_payload = payload
                    await user.save()
                logger.info(
                    f"New user [ID:{user.pk}] [USERNAME:@{user.username}] "
                    f"with {user.start_payload=}"
                )
            else:
                # Update the user once a day
                if user.date_updated < arrow.Arrow.utcnow().shift(days=-1).datetime:
                    await user.update_from_dict(msg.from_user.to_python()).save()
                    logger.debug(f"User [ID:{user.pk}] updated")
                # Update the user when they send their contact
                elif msg.contact and msg.contact.user_id == user.id:
                    await user.update_from_dict(msg.contact.to_python()).save()
                    logger.debug(f"User [ID:{user.pk}] updated")

        except Exception as e:
            logger.error(f"Exception in {self.__class__.__name__}: {e} ({e.__class__}")
            raise e

        message = await self._save_message(msg)
        logger.info(f"Logged message [ID:{message.pk}] in chat [{msg.chat.type}:{msg.chat.id}]")

    async def on_post_process_message(
        self, msg: types.Message, response_msgs: list[types.Message], *_, **__
    ):
        """Mark the original message as handled and save the bot's messages into the database."""
        # Mark the original message as handled
        if response_msgs:
            message = await Message.get(message_id=msg.message_id, chat_id=msg.chat.id)
            message.is_handled = True
            await message.save()

        # Save the response messages
        for response_msg in response_msgs:
            if isinstance(response_msg, types.Message):
                response_message = await self._save_message(response_msg)
                logger.info(
                    f"Logged response message [ID:{response_message.pk}] "
                    f"in chat [{msg.chat.type}:{msg.chat.id}]"
                )
            else:
                logger.warning(
                    f"Response message is not a Message: {response_msg.__class__}: "
                    f"{response_msg.to_python()=}"
                )
