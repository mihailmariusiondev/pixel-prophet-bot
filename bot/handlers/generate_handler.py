from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import logging

# Diccionario para almacenar las colas de prompts por usuario
user_queues = {}
# Diccionario para rastrear si un usuario está procesando actualmente
processing_status = {}


async def generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /generate command to create images from text.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Generate command received from user {user_id} ({username})")

    # Extract prompt from message
    prompt = (
        update.message.text.split(" ", 1)[1]
        if len(update.message.text.split(" ", 1)) > 1
        else ""
    )

    # Validate prompt presence
    if not prompt:
        logging.warning(f"Empty prompt received from user {user_id}")
        await update.message.reply_text(
            "Por favor, proporciona un prompt para generar la imagen."
        )
        return

    try:
        # Generate image and send results
        await ReplicateService.generate_image(
            prompt, user_id=user_id, message=update.message
        )

    except Exception as e:
        logging.error(
            f"Error in generate_handler for user {user_id}: {str(e)}", exc_info=True
        )
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta más tarde."
        )
