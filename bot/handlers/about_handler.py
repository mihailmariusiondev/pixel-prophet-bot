from telegram import Update
from telegram.ext import ContextTypes
import logging


async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /about command to display information about the bot and its creator.
    Provides basic information and donation details.

    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"About command requested by user {user_id} ({username})")

    try:
        about_text = (
            "PixelProphetBot: genera imágenes de texto\n"
            "Creador: @Arkantos2374\n"
            "Dona: paypal.me/mariusmihailion"
        )

        await update.message.reply_text(about_text)
        logging.debug(f"About information sent to user {user_id}")
    except Exception as e:
        logging.error(
            f"Error sending about information to user {user_id}: {e}", exc_info=True
        )
        await update.message.reply_text(
            "❌ Error al mostrar la información. Por favor, intenta nuevamente."
        )
