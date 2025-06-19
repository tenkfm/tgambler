from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from app.settings import Settings

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "🎮 Let's roll!",
                    url=f"https://t.me/{Settings().bot_username}?startapp=main"  # обычная URL-кнопка
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

    # Отправляем картинку
    await update.message.reply_photo(
        photo="https://pub-37566c15883f4181ba07f58dcd29900d.r2.dev/bot/title.jpg",
        caption=text,
        reply_markup=reply_markup
    )

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Commands:\n/start — Launch\n/help — Help")

# Создание и запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(Settings().telegram_bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()


