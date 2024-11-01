from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
from ..utils.database import db
import logging
from ..utils.decorators import require_configured
import asyncio
import random
import json
import replicate
from ..utils import format_generation_message


@require_configured
async def variations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generates 3 variations of existing images based on their prompts.
    """
    try:
        user_id = update.effective_user.id
        # Get prompt from specific prediction or last generation
        if context.args:
            prediction_data = await db.get_prediction(context.args[0])
            if not prediction_data:
                await update.message.reply_text(
                    "❌ No se encontraron datos para esta predicción."
                )
                return
            prompt = prediction_data[0]
        else:
            last_prediction = await db.get_last_prediction(user_id)
            if not last_prediction:
                await update.message.reply_text("❌ No hay una generación previa.")
                return
            prompt = last_prediction[1]

        status_message = await update.message.reply_text("⏳ Generando variaciones...")

        # Generate 3 variations concurrently
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    ReplicateService.generate_image(
                        prompt,
                        user_id=user_id,
                        message=update.message,
                        operation_type="variation",
                    )
                )
                for _ in range(3)
            ]

        await status_message.delete()
    except Exception as e:
        logging.error(f"Error in variations_handler - User: {user_id}", exc_info=True)
        if "status_message" in locals():
            await status_message.edit_text("❌ Error al generar las variaciones.")
