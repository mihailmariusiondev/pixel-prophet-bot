# bot/handlers/generate_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import logging
from ..utils.decorators import require_configured
from ..utils.database import Database

db = Database()


@require_configured
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
    logging.info(f"Extracted prompt for user {user_id}: '{prompt}'")
    # Validate prompt presence
    if not prompt:
        logging.warning(f"Empty prompt received from user {user_id}")
        await update.message.reply_text(
            "Por favor, proporciona un prompt para generar la imagen."
        )
        return
    try:
        # Fetch user configuration
        config = db.get_user_config(user_id, ReplicateService.default_params.copy())
        trigger_word = config.get("trigger_word")
        model_endpoint = config.get("model_endpoint")
        logging.info(
            f"User {user_id} configuration fetched: Trigger Word='{trigger_word}', Model Endpoint='{model_endpoint}'"
        )

        # Optionally, prepend trigger_word to the prompt
        full_prompt = f"{trigger_word} {prompt}"
        logging.info(
            f"Full prompt for image generation for user {user_id}: '{full_prompt}'"
        )

        # Generate image and send results
        await ReplicateService.generate_image(
            full_prompt, user_id=user_id, message=update.message
        )
        logging.info(f"Image generation initiated for user {user_id}")
    except Exception as e:
        logging.error(
            f"Error in generate_handler for user {user_id}: {str(e)}", exc_info=True
        )
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta más tarde."
        )
