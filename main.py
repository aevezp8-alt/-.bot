import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ============================
# НАСТРОЙКИ — ЗАПОЛНИ СЮДА
# ============================
BOT_TOKEN = "8020218518:AAF3DIBLNFCP0YwRbUzDqiOgRPsdwwtAwB8"   # Получить у @BotFather
ADMIN_ID = 8318310777                    # Telegram ID админа
# ============================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# /start — приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Это приём сообщений vorrxy.\n"
        "Напишите ваше сообщение"
    )

# Любое обычное сообщение — пересылаем админу
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    # Формируем подпись: имя + username + ID
    name = user.full_name or "Без имени"
    username = f"@{user.username}" if user.username else "нет username"
    user_info = f"👤 {name} ({username})\n🆔 ID: {user.id}\n\n"

    try:
        # Пересылаем оригинальное сообщение (текст, фото, голос и т.д.)
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id
        )
        # Отдельно шлём инфу об отправителе
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⬆️ Сообщение от:\n{user_info}"
                 f"Чтобы ответить — перешли это сообщение обратно боту (reply)."
        )
    except Exception as e:
        logging.error(f"Ошибка пересылки: {e}")

    # Подтверждение пользователю
    await msg.reply_text("✅ Сообщение получено! Скоро с вами свяжутся.")


# Команда /reply для ответа пользователю (только для админа)
# Использование: переслать сообщение пользователя → ответить /reply Текст ответа
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return  # только админ

    if not update.message.reply_to_message:
        await update.message.reply_text("Ответь реплаем на пересланное сообщение и напиши /reply текст")
        return

    # Получаем ID пользователя из пересланного сообщения
    fwd = update.message.reply_to_message.forward_origin
    if fwd and hasattr(fwd, "sender_user"):
        target_id = fwd.sender_user.id
    elif update.message.reply_to_message.forward_from:
        target_id = update.message.reply_to_message.forward_from.id
    else:
        await update.message.reply_text("❌ Не могу определить получателя. Убедись, что пересылаешь сообщение от пользователя.")
        return

    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Напиши текст после /reply")
        return

    try:
        await context.bot.send_message(chat_id=target_id, text=f"💬 Ответ от администратора:\n\n{text}")
        await update.message.reply_text("✅ Ответ отправлен!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_to_user))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_admin))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
