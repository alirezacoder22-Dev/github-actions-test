import os
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)


# =========================
# CONFIG
# =========================

TOKEN = os.environ["BOT_TOKEN"]

# Chat ID / User ID ادمین
ADMIN_CHAT_ID = 7122415157

# Render PORT
PORT = int(os.environ.get("PORT", 8000))


# =========================
# SIMPLE HTTP SERVER
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.end_headers()

        self.wfile.write(
            "Bot is alive!".encode("utf-8")
        )

    def log_message(self, format, *args):
        # جلوگیری از لاگ‌های اضافی HTTP
        pass


def run_web_server():
    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )

    print(f"🌐 HTTP server running on port {PORT}")

    server.serve_forever()


# اجرای وب‌سرور در Thread جدا
threading.Thread(
    target=run_web_server,
    daemon=True
).start()


# =========================
# REPLY SYSTEM
# =========================

# اینجا ذخیره می‌کنیم:
# admin_id -> user_id
pending_replies = {}


# =========================
# HANDLE "REPLY" BUTTON
# =========================

async def reply_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    # فقط ادمین اجازه پاسخ دارد
    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer(
            "⛔ دسترسی ندارید",
            show_alert=True
        )
        return

    await query.answer()

    # callback_data:
    # reply_USER_ID

    data = query.data

    if not data.startswith("reply_"):
        return

    try:
        user_id = int(
            data.replace("reply_", "")
        )
    except ValueError:
        return

    # ذخیره کاربری که قرار است جواب بگیرد
    pending_replies[ADMIN_CHAT_ID] = user_id

    await query.message.reply_text(
        "✏️ پاسخ خودت رو بنویس.\n\n"
        "پیام بعدی تو برای همین کاربر ارسال میشه."
    )


# =========================
# HANDLE MESSAGES
# =========================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    user = update.effective_user
    message = update.message

    # =====================================
    # ADMIN MESSAGE
    # =====================================

    if user and user.id == ADMIN_CHAT_ID:

        # اگر ادمین در حالت پاسخ باشد
        if ADMIN_CHAT_ID in pending_replies:

            target_user_id = pending_replies.pop(
                ADMIN_CHAT_ID
            )

            if message.text:

                try:

                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=message.text
                    )

                    await message.reply_text(
                        "✅ پاسخ ارسال شد."
                    )

                except Exception as e:

                    await message.reply_text(
                        f"❌ ارسال پاسخ ناموفق بود:\n{e}"
                    )

            else:

                await message.reply_text(
                    "⚠️ فعلاً فقط پیام متنی قابل ارسال است."
                )

            return

        # اگر ادمین در حالت پاسخ نیست
        if message.text:
            await message.reply_text(
                message.text
            )

        return


    # =====================================
    # USER MESSAGE
    # =====================================

    full_name = (
        user.full_name
        if user
        else "نام نامشخص"
    )

    username = (
        f"@{user.username}"
        if user and user.username
        else "ندارد"
    )

    user_id = (
        user.id
        if user
        else "نامشخص"
    )

    text = (
        message.text
        if message.text
        else "[پیام غیرمتنی]"
    )

    # زمان UTC
    time = datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    # =====================================
    # REPLY BUTTON
    # =====================================

    keyboard = [
        [
            InlineKeyboardButton(
                "💬 پاسخ",
                callback_data=f"reply_{user_id}"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(
        keyboard
    )

    # =====================================
    # ADMIN REPORT
    # =====================================

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
        text=admin_message,
        reply_markup=reply_markup
    )

    # =====================================
    # NORMAL ECHO
    # =====================================

    if message.text:

        await message.reply_text(
            message.text
        )


# =========================
# APPLICATION
# =========================

app = (
    Application
    .builder()
    .token(TOKEN)
    .build()
)


# پیام‌های معمولی
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)


# دکمه پاسخ
app.add_handler(
    CallbackQueryHandler(
        reply_button
    )
)


# =========================
# START
# =========================

print("🤖 Bot is running...")
print(f"🌐 Web server port: {PORT}")

app.run_polling()
