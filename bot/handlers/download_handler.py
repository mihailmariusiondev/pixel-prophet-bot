from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import logging


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /download command to download all predictions.
    Downloads and saves all generated images from Replicate to local storage.

    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Download command received from user {user_id} ({username})")

    try:
        # Send initial status message
        message = await update.message.reply_text(
            "⏳ Recopilando predicciones de todas las páginas..."
        )
        logging.info(f"Starting batch download process for user {user_id}")

        # Download all predictions
        logging.debug("Initiating batch download of all predictions")
        count = await ReplicateService.download_all_predictions()
        logging.info(f"Successfully downloaded {count} predictions")

        # Update status message with results
        success_message = (
            f"✅ Descarga completada.\n"
            f"Se procesaron {count} imágenes de todas las páginas disponibles."
        )
        await message.edit_text(success_message)
        logging.info(f"Download completed for user {user_id} - {count} images processed")

    except Exception as e:
        error_msg = f"Error in download_handler for user {user_id}: {e}"
        logging.error(error_msg, exc_info=True)

        # Send error message to user
        await update.message.reply_text(
            "❌ Ocurrió un error al descargar las predicciones. Por favor, intenta más tarde."
        )
