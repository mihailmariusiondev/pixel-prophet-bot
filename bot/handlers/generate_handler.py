# bot/handlers/generate_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import logging
from ..utils.decorators import require_configured
from ..utils.database import db
import asyncio

@require_configured
async def generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles single image generation from text prompt.
    Validates input and delegates to ReplicateService for generation.

    Args:
        update: Telegram update containing the message and user info
        context: Bot context for maintaining state

    Flow:
    1. Extracts prompt from message
    2. Validates prompt is not empty
    3. Delegates to ReplicateService for image generation
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Generate command received - User: {user_id} ({username})")

    # Extract prompt from message, splitting on first space
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

    logging.info(f"Starting image generation - User: {user_id}, Prompt: {prompt[:100]}...")
    try:
        asyncio.create_task(
            ReplicateService.generate_image(
                prompt,
                user_id=user_id,
                message=update.message,
                operation_type="single"
            )
        )
        logging.info(f"Image generation completed successfully - User: {user_id}")
    except Exception as e:
        logging.error(f"Failed to generate image - User: {user_id}, Error: {str(e)}", exc_info=True)
        await update.message.reply_text("❌ Error al generar la imagen. Por favor, intenta nuevamente.")
