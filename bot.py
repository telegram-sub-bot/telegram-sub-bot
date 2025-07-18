import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import ChatAdminRequired

import logging
import os

# Чтение токена из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID твоего канала
CHANNEL_ID = -1002317263713

# ID двух групп, где работает бот
ALLOWED_GROUPS = [-1001363070158, -1001995633215]

# Кнопка підписки
SUBSCRIBE_BUTTON = InlineKeyboardMarkup().add(
    InlineKeyboardButton("📲 Підписатися", url="https://t.me/+326rbR1CM8QwMThi")
)

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status != "left"
    except:
        return False

@dp.message_handler(lambda message: message.chat.id in ALLOWED_GROUPS)
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Не чіпаємо адмінів та ботів
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status in ["administrator", "creator"] or message.from_user.is_bot:
            return
    except:
        return

    if not await is_subscribed(user_id):
        try:
            # Видаляємо повідомлення користувача
            await message.delete()

            # Підпис з ім’ям
            name = message.from_user.first_name or "користувач"
            caption = (
                f"🔒 {name}, щоб писати в групі, потрібно бути підписаним на канал.\n"
                f"👇 Натисни кнопку нижче для підписки:"
            )

            # Надсилаємо зображення з підписом та кнопкою
            reply = await bot.send_photo(
                chat_id=chat_id,
                photo="https://i.postimg.cc/66kjh8c4/Polish-20250718-115606708.jpg",
                caption=caption,
                reply_markup=SUBSCRIBE_BUTTON
            )

            # Видаляємо це повідомлення через 10 секунд
            await asyncio.sleep(20)
            await reply.delete()

        except ChatAdminRequired:
            pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
