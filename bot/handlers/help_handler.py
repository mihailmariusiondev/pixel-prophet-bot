from telegram import Update
from telegram.ext import ContextTypes


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Define the help message with available commands
    help_handler_text = (
        "Este bot hace cosas.\n"
        "Comandos disponibles:\n"
        "/start - Iniciar el bot\n"
        "/help - Mostrar este mensaje de ayuda\n"
        "/about - Información sobre el bot\n"
    )
    # Send the help message to the user
    await update.message.reply_text(help_handler_text)
