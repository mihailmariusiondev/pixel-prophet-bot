from telegram import Update
from telegram.ext import ContextTypes
import logging
import json
from ..utils.database import Database
import replicate
from ..utils import format_generation_message

db = Database()


async def last_generation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /last_generation command to show details of the last generated image"""
    try:
        predictions_page = replicate.predictions.list()
        if not predictions_page.results:
            await update.message.reply_text(
                "❌ No se encontró la información de la última predicción."
            )
            return

        latest_prediction = predictions_page.results[0]
        image_url = (
            latest_prediction.output[0]
            if isinstance(latest_prediction.output, list)
            else latest_prediction.output
        )

        await update.message.reply_text(
            format_generation_message(
                image_url,
                latest_prediction.id,
                json.dumps(latest_prediction.input, indent=2),
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(f"Error en last_generation_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error al recuperar la última generación."
        )
