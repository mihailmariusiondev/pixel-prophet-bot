from telegram import Update
from telegram.ext import ContextTypes


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Define the start message
    start_text = "¡Hola! Me has iniciado"
    # Send the start message to the user
    await update.message.reply_text(start_text)
