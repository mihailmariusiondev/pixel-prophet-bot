# bot/handlers/start_handler.py

from telegram import Update
from telegram.ext import ContextTypes
import logging


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initial entry point for new users interacting with the bot.
    Handles the /start command and provides a welcome message with basic instructions.
    Args:
        update: Telegram update object containing message info
        context: Bot context for maintaining state
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    chat_id = update.effective_chat.id
    # Log the new user interaction with detailed context
    logging.info(
        f"New user started bot - ID: {user_id}, Username: {username}, Chat: {chat_id}"
    )
    # Multi-line welcome message using string concatenation for better readability
    welcome_text = (
        "¡Bienvenido a PixelProphetBot! 🎨✨\n\n"
        "Soy un bot que genera imágenes únicas basadas en tus descripciones de texto.\n\n"
        "Antes de comenzar, por favor configura los siguientes parámetros esenciales:\n"
        "1. **Palabra Clave (Trigger Word)**: Necesaria para el entrenamiento LoRA.\n"
        "2. **Endpoint del Modelo**: Endpoint de la API del modelo para la generación de imágenes.\n\n"
        "Puedes configurar estos parámetros usando el comando `/config`.\n"
        "Por ejemplo:\n"
        "• `/config trigger_word MARIUS`\n"
        "• `/config model_endpoint mihailmariusiondev/marius-flux:422d4bddab17dadb069e1956009fd55d58ba6c8fd5c8d4a071241b36a7cba3c7`\n\n"
        "¡Una vez configurados, estarás listo para comenzar a crear!"
    )
    try:
        logging.debug(f"Sending welcome message to user {user_id}")
        await update.message.reply_text(welcome_text, parse_mode="Markdown")
        logging.info(f"Welcome message sent successfully to user {user_id}")
    except Exception as e:
        logging.error(
            f"Error sending welcome message to user {user_id} in chat {chat_id}: {str(e)}",
            exc_info=True,
        )
        await update.message.reply_text(
            "❌ Error al mostrar el mensaje de bienvenida. Por favor, intenta nuevamente con /start."
        )
