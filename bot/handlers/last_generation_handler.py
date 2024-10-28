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
    user_id = update.effective_user.id
    logging.info(f"Last generation request from user {user_id}")

    try:
        logging.debug("Fetching predictions from Replicate")
        predictions_page = replicate.predictions.list()

        if not predictions_page.results:
            logging.warning("No predictions found in Replicate")
            await update.message.reply_text(
                "❌ No se encontró la información de la última predicción."
            )
            return

        latest_prediction = predictions_page.results[0]
        logging.info(f"Retrieved latest prediction ID: {latest_prediction.id}")

        image_url = (
            latest_prediction.output[0]
            if isinstance(latest_prediction.output, list)
            else latest_prediction.output
        )

        logging.debug(f"Formatting message for prediction {latest_prediction.id}")
        await update.message.reply_text(
            format_generation_message(
                image_url,
                latest_prediction.id,
                json.dumps(latest_prediction.input, indent=2),
            ),
            parse_mode="Markdown",
        )
        logging.info(f"Successfully sent last generation info to user {user_id}")

    except Exception as e:
        logging.error(
            f"Error in last_generation_handler for user {user_id}: {e}", exc_info=True
        )
        await update.message.reply_text(
            "❌ Ocurrió un error al recuperar la última generación."
        )
