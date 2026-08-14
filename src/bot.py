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
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    user = update.effective_user
    message = update.message

    # اطلاعات کاربر
    full_name = user.full_name or "نام نامشخص"
    username = f"@{user.username}" if user.username else "ندارد"
    user_id = user.id

    # زمان
    time = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    # متن پیام
    text = message.text or "[پیام غیرمتنی]"

    # پیام اطلاع‌رسانی برای ادمین
    admin_message = (
        "📩 پیام جدید!\n\n"
        f"👤 نام: {full_name}\n"
        f"🔹 Username: {username}\n"
        f"🆔 ID: {user_id}\n"
        f"🕐 زمان: {time}\n\n"
        "💬 پیام:\n"
        f"{text}"
    )

    # ارسال اطلاع به ادمین
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_message
    )


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.ALL & ~filters.COMMAND,
        handle_message
    )
)

print("Bot is running...")

app.run_polling()
