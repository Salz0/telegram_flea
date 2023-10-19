"""The models used in the application."""

from __future__ import annotations

from tortoise import fields

from utils.tortoise_orm import Model


class BaseModel(Model):
    """The base model for all models."""

    date_added = fields.DatetimeField(auto_now_add=True)
    date_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        """The metaclass for the base model."""

        abstract = True


# region Telegram models
class User(BaseModel):
    """
    The model for the Telegram user.

    This model stores all the information about the user.
    It is also used to store all the authentication-related information.
    """

    id = fields.BigIntField(pk=True, generated=False)

    username = fields.CharField(max_length=32, null=True)

    first_name = fields.TextField(null=True)
    last_name = fields.TextField(null=True)

    phone_number = fields.CharField(max_length=14, null=True)
    language_code = fields.CharField(max_length=2, null=True)
    is_bot = fields.BooleanField(default=False)

    start_payload = fields.TextField(null=True)

    is_active = fields.BooleanField(default=True)
    has_bot_blocked = fields.BooleanField(default=False)
    is_beta = fields.BooleanField(default=False)
    is_deleted = fields.BooleanField(default=False)

    is_admin = fields.BooleanField(default=False)
    is_staff_member = fields.BooleanField(default=False)

    messages: fields.ReverseRelation[Message]

    @property
    def full_name(self):
        """Get the full name of the user."""
        if not self.last_name:
            return self.first_name

        return f"{self.first_name} {self.last_name}"


class Message(BaseModel):
    """The model for the Telegram message."""

    from_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "bot.User", related_name="messages"
    )

    # In Telegram, `message_id` is unique only **within a chat**.
    message_id = fields.BigIntField()  # for the sake of safety, this is a `BigIntField`

    # TODO: [3/20/2023 by Mykola] Make this a foreign key to the Chat model
    chat_id = fields.BigIntField()

    reply_to_message: fields.ForeignKeyRelation[Message] = fields.ForeignKeyField(
        "bot.Message", related_name="replies", null=True
    )

    content_type = fields.TextField(null=True)
    text = fields.TextField(null=True)

    date = fields.DatetimeField()
    is_handled = fields.BooleanField(default=False)

    complete_message_json = fields.JSONField(null=True)

    replies: fields.BackwardFKRelation[Message]


# endregion
