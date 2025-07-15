import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import ChatAdminRequired, CantRestrictSelf

import logging
import os

# Чтение токена из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID твоего канала
CHANNEL_ID = -1002317263713

# ID двух групп, где работает бот
ALLOWED_GROUPS = [-1001363070158, -1001995633215]

# Текст уведомления
WARNING_TEXT = (
    "🔒 Щоб писати в групі, потрібно бути підписаним на канал.\n"
    "👇 Натисни кнопку нижче для підписки:"
)

# Кнопка підписки
SUBSCRIBE_BUTTON = InlineKeyboardMarkup().add(
    InlineKeyboardButton("📲 Підписатися", url="https://t.me/+IsSgAN3CDshmM2IyID")
)

# Права після підписки (дозволяє писати)
PERMISSIONS_FULL = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_invite_users=True,
)

# Права до підписки (забороняє писати)
PERMISSIONS_RESTRICTED = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_invite_users=False,
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
async def restrict_if_not_subscribed(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Не чіпаємо адмінів та ботів
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status in ["administrator", "creator"] or message.from_user.is_bot:
            return
    except:
        return

    # Перевіряємо підписку
    if not await is_subscribed(user_id):
        try:
            # Обмежуємо користувача
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=PERMISSIONS_RESTRICTED
            )

            # Видаляємо його повідомлення
            await message.delete()

            # Відповідаємо в групі з кнопкою підписки
            await bot.send_message(chat_id, WARNING_TEXT, reply_markup=SUBSCRIBE_BUTTON)

        except (ChatAdminRequired, CantRestrictSelf):
            pass
    else:
        # Якщо підписаний — знімаємо обмеження
        try:
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=PERMISSIONS_FULL
            )
        except:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
