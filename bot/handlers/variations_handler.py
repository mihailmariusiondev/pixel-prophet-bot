from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
from ..utils.database import db
import logging
from ..utils.decorators import require_configured
import asyncio
import json


@require_configured
async def variations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generates variations of existing images based on their prompts.
    Can work with specific prediction ID or last generation.

    Args:
        update: Telegram update containing the message and user info
        context: Bot context containing optional prediction ID

    Flow:
    1. Checks for specific prediction ID in args
    2. If no ID, uses last generation
    3. Generates 3 variations using original prompt
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Variations requested - User: {user_id} ({username})")

    try:
        # Get prompt from previous generation or args
        if context.args:
            prediction_id = context.args[0]
            prediction_data = await db.get_prediction(prediction_id)
            if not prediction_data:
                await update.message.reply_text("❌ No se encontraron datos para esta predicción.")
                return
            prompt = prediction_data[0]
        else:
            last_prediction = await db.get_last_prediction(user_id)
            if not last_prediction:
                await update.message.reply_text("❌ No hay una generación previa.")
                return
            prompt = last_prediction[0]

        # Generate variations concurrently
        tasks = []
        for _ in range(3):
            task = asyncio.create_task(
                ReplicateService.generate_image(
                    prompt,
                    user_id=user_id,
                    message=update.message,
                    operation_type="variation",
                )
            )
            tasks.append(task)

        # Wait for all generations to complete
        image_urls = await asyncio.gather(*tasks)
        image_urls = [url for url in image_urls if url]  # Filter out any failed generations

        if not image_urls:
            await update.message.reply_text("❌ No se pudieron generar variaciones.")
            return

        # Save predictions and send details to user
        await ReplicateService.save_predictions_for_images(
            image_urls,
            user_id,
            prompt,
            update.message
        )

    except Exception as e:
        logging.error(f"Error in variations_handler: {e}")
        await update.message.reply_text("❌ Ocurrió un error al generar las variaciones.")
