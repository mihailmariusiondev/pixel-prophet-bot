from telegram import Update
from telegram.ext import ContextTypes
import logging


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initial entry point for new users interacting with the bot.
    Provides a friendly welcome message and basic usage instructions.
    """
    user_id = update.effective_user.id
    logging.info(f"New user started the bot: {user_id}")

    # Multi-line welcome message using string concatenation for better readability
    # Includes emoji for visual appeal and an example to help users get started
    welcome_text = (
        "¡Bienvenido a PixelProphetBot! 🎨✨\n\n"
        "Soy un bot que genera imágenes únicas basadas en tus descripciones de texto.\n\n"
        "Para comenzar, simplemente usa el comando /generate seguido de tu descripción.\n"
        "Por ejemplo: /generate un gato jugando ajedrez en la luna\n\n"
        "¡Diviértete explorando tu creatividad!"
    )

    try:
        await update.message.reply_text(welcome_text)
        logging.debug(f"Welcome message sent to user {user_id}")
    except Exception as e:
        logging.error(
            f"Error sending welcome message to user {user_id}: {e}", exc_info=True
        )
