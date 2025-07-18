import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import ChatAdminRequired

# Чтение токена из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID твоего канала
CHANNEL_ID = -1002317263713

# ID групп, где работает бот
ALLOWED_GROUPS = [-1001363070158, -1001995633215, -1002096496817]

# Кнопка підписки
SUBSCRIBE_BUTTON = InlineKeyboardMarkup().add(
    InlineKeyboardButton("📲 ✅️ ПІДПИСАТИСЬ ✅️", url="https://t.me/+326rbR1CM8QwMThi")
)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Проверка подписки пользователя на канал
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status != "left"
    except:
        return False

# Обработка всех сообщений в разрешённых группах
@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_all_messages(message: types.Message):
    if message.chat.id not in ALLOWED_GROUPS:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    # Пропускаем админов и ботов
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status in ["administrator", "creator"] or message.from_user.is_bot:
            return
    except:
        return

    if not await is_subscribed(user_id):
        try:
            # Удаляем сообщение пользователя
            await message.delete()

            # Имя пользователя
            name = message.from_user.first_name or "користувач"

            # Предупреждение
            warning_text = (
                f"🔒 {name}, щоб писати в групі, потрібно бути підписаним на канал.\n"
                f"👇 Натисни кнопку нижче для підписки:"
            )

            # Фото-напоминание
            image_url = "https://i.postimg.cc/66kjh8c4/Polish-20250718-115606708.jpg"
            reply = await bot.send_photo(
                chat_id,
                photo=image_url,
                caption=warning_text,
                reply_markup=SUBSCRIBE_BUTTON
            )

            # Удаление напоминания через 20 сек
            await asyncio.sleep(20)
            await reply.delete()

        except ChatAdminRequired:
            pass

# Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
