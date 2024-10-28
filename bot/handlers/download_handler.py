from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import logging


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /download command to download all predictions"""
    user_id = update.effective_user.id
    logging.info(f"Download command received from user {user_id}")

    try:
        # Enviar mensaje inicial
        message = await update.message.reply_text(
            "⏳ Recopilando predicciones de todas las páginas..."
        )
        logging.info("Starting batch download of all predictions")

        # Obtener y descargar predicciones
        count = await ReplicateService.download_all_predictions()
        logging.info(f"Successfully downloaded {count} predictions")

        # Actualizar mensaje con el resultado
        await message.edit_text(
            f"✅ Descarga completada.\n"
            f"Se procesaron {count} imágenes de todas las páginas disponibles."
        )

    except Exception as e:
        logging.error(
            f"Error in download_handler for user {user_id}: {e}", exc_info=True
        )
        await update.message.reply_text(
            "❌ Ocurrió un error al descargar las predicciones. Por favor, intenta más tarde."
        )
