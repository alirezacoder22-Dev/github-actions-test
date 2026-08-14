import os
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]

# Chat ID / User ID ادمین
ADMIN_CHAT_ID = 7122415157


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    user = update.effective_user
    message = update.message
    text = message.text or "[پیام غیرمتنی]"

    # اگر خود ادمین پیام داده باشد:
    # فقط مثل یک Echo Bot عادی جواب بده
    if user and user.id == ADMIN_CHAT_ID:
        if message.text:
            await message.reply_text(message.text)
        return

    # اطلاعات فرستنده
    full_name = user.full_name if user else "نام نامشخص"
    username = f"@{user.username}" if user and user.username else "ندارد"
    user_id = user.id if user else "نامشخص"

    # زمان UTC
    time = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    # گزارش برای ادمین
    admin_message = (
        "📩 پیام جدید!\n\n"
        f"👤 نام: {full_name}\n"
        f"🔹 Username: {username}\n"
        f"🆔 ID: {user_id}\n"
        f"🕐 زمان: {time}\n\n"
        "💬 پیام:\n"
        f"{text}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_message
    )

    # Echo عادی برای کاربر
    if message.text:
        await message.reply_text(message.text)


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

print("Bot is running...")

app.run_polling()
