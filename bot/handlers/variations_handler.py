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
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        logging.info(f"Variations requested - User: {user_id} ({username})")

        # Get base configuration and validate
        params = await db.get_user_config(
            user_id, ReplicateService.default_params.copy()
        )
        trigger_word = params.get("trigger_word")
        model_endpoint = params.get("model_endpoint")
        if not trigger_word or not model_endpoint:
            await update.message.reply_text("❌ Configuración incompleta.")
            return

        # Get prompt from specific prediction or last generation
        if context.args:
            prediction_id = context.args[0]
            prediction_data = await db.get_prediction(prediction_id)
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
            prompt = last_prediction[0]

        # Send initial status message
        status_message = await update.message.reply_text("⏳ Generando variaciones...")

        # Prepare generation parameters for each variation
        variations = []
        for _ in range(3):
            variation_params = params.copy()
            variation_params["seed"] = random.randint(1, 1000000)
            variation_params["prompt"] = prompt
            variations.append(variation_params)

        # Generate variations concurrently
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(replicate.async_run(
                    variation_params["model_endpoint"],
                    input=variation_params
                ))
                for variation_params in variations
            ]

        # Get results and predictions
        results = [task.result() for task in tasks]
        predictions_page = replicate.predictions.list()  # This is not async
        recent_predictions = list(predictions_page)[:3]  # Convert page to list and get first 3

        # Save predictions to database
        for result, variation_params, prediction in zip(results, variations, recent_predictions):
            if result and result[0]:  # Check if we have a valid output URL
                await db.save_prediction(
                    prediction_id=prediction.id,
                    user_id=user_id,
                    prompt=prompt,
                    input_params=json.dumps(variation_params),
                    output_url=result[0]
                )
                # Send the variation with its details
                await update.message.reply_photo(
                    photo=result[0],
                    caption=format_generation_message(prediction.id, json.dumps(variation_params)),
                    parse_mode="Markdown"
                )

        # Clean up status message
        await status_message.delete()

    except Exception as e:
        logging.error(f"Error in variations_handler - User: {user_id}", exc_info=True)
        if "status_message" in locals():
            await status_message.edit_text("❌ Error al generar las variaciones.")
