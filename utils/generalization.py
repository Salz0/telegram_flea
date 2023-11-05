from aiogram import types

from models import Message


async def create_message_instance(message: types.Message, **extra_fields) -> Message:
    # Create a dictionary with the common fields.
    message_data = {
        "message_id": message.message_id,
        "from_user_id": message.from_user.id,
        "chat_id": message.chat.id,  # This assumes that chat ID is directly accessible.
        "text": message.text,
        "date": message.date,
        "is_handled": True,
        "complete_message_json": message.to_python(),
        "content_type": message.content_type,
    }
    message_data.update(extra_fields)
    return await Message.create(**message_data)

    # TODO: Add replied message relations to the database [04/11/2023 by Vladyslav Bilyk]
    # Create the Message instance with the combined data.
    # if message.reply_to_message:
    #     reply_to_message: tuple[Message, bool] = await create_message_instance(message.reply_to_message)
    #     message_data['reply_to_message_id'] = reply_to_message[0].message_id
    # message_data.update(extra_fields)
    # Add any additional fields that were passed in.
    # try:
    #     return await Message.get_or_create(**message_data)
    # except tortoise.exceptions.IntegrityError as e:
    #     logger.exception(e)
