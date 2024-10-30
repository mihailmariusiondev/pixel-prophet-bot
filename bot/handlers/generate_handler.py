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
    Handles single image generation from text prompt.
    Validates input and delegates to ReplicateService for generation.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Generate command received - User: {user_id} ({username})")

    # Extract and validate prompt
    prompt = (
        update.message.text.split(" ", 1)[1]
        if len(update.message.text.split(" ", 1)) > 1
        else ""
    )

    if not prompt:
        logging.warning(f"Empty prompt received - User: {user_id}")
        await update.message.reply_text(
            "Por favor, proporciona un prompt para generar la imagen."
        )
        return

    await ReplicateService.generate_image(
        prompt,
        user_id=user_id,
        message=update.message,
        operation_type="single"
    )
