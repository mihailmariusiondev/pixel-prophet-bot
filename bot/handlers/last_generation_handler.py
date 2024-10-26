from telegram import Update
from telegram.ext import ContextTypes
import logging
import json
from ..utils.database import Database
import replicate

db = Database()


async def last_generation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /last_generation command to show details of the last generated image"""
    try:
        user_id = update.effective_user.id
        last_gen = db.get_last_generation(user_id)

        if not last_gen:
            await update.message.reply_text(
                "❌ No hay una generación previa. Primero usa /generate para crear una imagen."
            )
            return

        # Obtener la última predicción
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

        detailed_message = (
            f"🔗 Image: {image_url}\n"
            f"📋 Prediction: https://replicate.com/p/{latest_prediction.id}\n\n"
            f"⚙️ Parameters:\n"
            f"```json\n{json.dumps(last_gen, indent=2)}\n```"
        )

        await update.message.reply_text(detailed_message, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error en last_generation_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error al recuperar la última generación."
        )
