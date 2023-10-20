import os

import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from dotenv import load_dotenv

load_dotenv()
bot = aiogram.Bot(os.environ["TELEGRAM_BOT_TOKEN"])
storage = MemoryStorage()
dp = aiogram.Dispatcher(bot, storage=storage)


# Define states
class SellItem(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_photo = State()


# Handlers
@dp.message_handler(aiogram.filters.CommandStart())
async def start(message: aiogram.types.Message):
    welcome_message = (
        f"👋 Welcome to Telegram Flea, the open-source flea-market bot!\n\n"
        f"This bot is designed to serve as a handy tool for university flea-markets"
        f"To get started, type /sell to put your item on sale or type /help for more information.\n\n"
        f"Happy buying and selling! 🎉"
    )
    await message.answer(welcome_message)


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
    print("here")
    await photo.download(destination_file="item_photo.jpg")

    # get data and reset state
    user_data = await state.get_data()
    await state.finish()

    # prepare data
    item_name = user_data.get("name")
    item_price = user_data.get("price")
    username = message.from_user.username or message.from_user.id

    caption = f"Item for sale:\n- Name: {item_name}\n- Price: {item_price}\n- Seller: @{username}"

    await bot.send_photo(
        "@" + os.environ["CHANNEL_USERNAME"],
        aiogram.types.InputFile("item_photo.jpg"),
        caption=caption,
    )
    await message.reply("Thank you! Your item is now for sale.")


if __name__ == "__main__":
    aiogram.executor.start_polling(dp)
