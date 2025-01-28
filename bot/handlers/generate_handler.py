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
    Handles concurrent image generation from text prompt.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Generate command received - User: {user_id} ({username})")

    # Extract prompt from message
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

    try:
        # Get user config to determine num_outputs
        config = await db.get_user_config(
            user_id, ReplicateService.default_params.copy()
        )
        num_outputs = config.get("num_outputs", 1)  # Default to 1 if not set

        # Un solo mensaje de estado según el número de imágenes
        status_text = (
            "⏳ Generando imagen..."
            if num_outputs == 1
            else f"⏳ Generando {num_outputs} imágenes..."
        )
        status_message = await update.message.reply_text(status_text)

        # Generate images concurrently
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    ReplicateService.generate_image(
                        prompt,
                        user_id=user_id,
                        message=update.message,
                        operation_type="single",
                    )
                )
                for _ in range(num_outputs)
            ]

        await status_message.delete()

    except Exception as e:
        logging.error(f"Error in generate_handler - User: {user_id}", exc_info=True)
        if "status_message" in locals():
            await status_message.edit_text("❌ Error al generar las imágenes.")
