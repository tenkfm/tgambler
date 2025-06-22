import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from app.settings import Settings
from bot.redis.redis_listener import listen_redis
from bot.redis.redis_listener_gift_withdrawer import listen_gift_withdrawer

# Gloab settings
settings = Settings()

# Start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "🎮 Let's roll!",
                    url=f"https://t.me/{settings.bot_username}?startapp=main"  # обычная URL-кнопка
            )

        ],
        [InlineKeyboardButton("🛟 Support", url="https://t.me/your_support_chat")],
        [InlineKeyboardButton("📄 User Agreement", url="https://yourdomain.com/agreement")],
        [InlineKeyboardButton("👥 Community", url="https://t.me/your_community")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "🎁 Try your luck in daily gift raffles at @case 🎮\n"
        "✨ Open cases and win amazing prizes every day!"
    )

    await update.message.reply_photo(
        photo="https://pub-37566c15883f4181ba07f58dcd29900d.r2.dev/bot/title.jpg",
        caption=text,
        reply_markup=reply_markup
    )

# Help handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Commands:\n/start — Launch\n/help — Help")

# Bot launch
if __name__ == "__main__":
    settings = Settings()
    app = ApplicationBuilder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # ✅ добавляем Redis listener как startup callback
    async def on_startup(app_):
        asyncio.create_task(listen_redis(app_))
        asyncio.create_task(listen_gift_withdrawer(app_))

    app.post_init = on_startup

    # 🟢 запуск без asyncio.run — run_polling сам всё сделает
    app.run_polling()

# nohup python -m bot.main > bot.log 2>&1 &
# pkill -f "python -m bot.main"
# 311213066