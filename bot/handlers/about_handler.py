from telegram import Update
from telegram.ext import ContextTypes
import logging


async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /about command to display information about the bot and its creator.
    Provides basic information and donation details.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    chat_id = update.effective_chat.id

    logging.info(f"About command requested by user {user_id} ({username}) in chat {chat_id}")

    try:
        logging.debug(f"Preparing about information for user {user_id}")
        about_text = (
            "PixelProphetBot: genera imágenes de texto\n"
            "Creador: @Arkantos2374\n"
            "Dona: paypal.me/mariusmihailion"
        )

        logging.debug(f"Sending about information to user {user_id}")
        await update.message.reply_text(about_text)
        logging.info(f"About information successfully sent to user {user_id}")

    except Exception as e:
        logging.error(
            f"Error sending about information to user {user_id} in chat {chat_id}: {str(e)}",
            exc_info=True
        )
        await update.message.reply_text(
            "❌ Error al mostrar la información. Por favor, intenta nuevamente."
        )
