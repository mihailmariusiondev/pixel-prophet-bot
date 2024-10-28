from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import logging


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles batch downloading of all predictions from Replicate.
    Downloads images to configured OneDrive path with standardized naming.
    Provides progress updates to user during the process.
    """
    user_id = update.effective_user.id
    logging.info(f"Download command received from user {user_id}")

    try:
        # Send initial status message
        message = await update.message.reply_text(
            "⏳ Recopilando predicciones de todas las páginas..."
        )
        logging.info("Starting batch download of all predictions")

        # Initiate download process through ReplicateService
        count = await ReplicateService.download_all_predictions()
        logging.info(f"Successfully downloaded {count} predictions")

        # Update user with final status
        await message.edit_text(
            f"✅ Descarga completada.\n"
            f"Se procesaron {count} imágenes de todas las páginas disponibles."
        )

    except Exception as e:
        # Handle any errors during download process
        logging.error(f"Error in download_handler for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error al descargar las predicciones. Por favor, intenta más tarde."
        )
