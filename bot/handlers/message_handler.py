from telegram import Update
from telegram.ext import ContextTypes

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Respond to any text message received
    await update.message.reply_text("Recibí tu mensaje de texto.")


