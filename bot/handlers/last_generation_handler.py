from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..utils.database import db
from ..utils.message_utils import format_generation_message
from ..utils.decorators import require_configured


@require_configured
async def last_generation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows the user's last generated image.
    """
    user_id = update.effective_user.id
    try:
        last_prediction = await db.get_last_prediction(user_id)
        if not last_prediction:
            await update.message.reply_text("❌ No hay generaciones previas.")
            return

        _, prompt, image_url, prediction_id = last_prediction  # Actualizado para incluir prediction_id
        await format_generation_message(prompt, update.message, image_url, prediction_id)

    except Exception as e:
        logging.error(f"Error retrieving last generation for user {user_id}: {e}")
        await update.message.reply_text("❌ Error al recuperar la última generación.")
