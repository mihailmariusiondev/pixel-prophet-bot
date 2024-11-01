# bot/handlers/generate_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
from ..utils.database import db
import logging
from ..utils.decorators import require_configured


@require_configured
async def generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /generate command to create images from text prompts.
    Args:
        update: Telegram update containing the message
        context: Bot context containing the prompt text
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Generate command received from user {user_id} ({username})")

    try:
        # Check if prompt was provided
        if not context.args:
            await update.message.reply_text(
                "❌ Por favor, proporciona un prompt después del comando.\n"
                "Ejemplo: `/generate un gato espacial`"
            )
            return

        # Join args to create prompt
        prompt = " ".join(context.args)
        logging.info(f"Generating image for prompt: {prompt} - User: {user_id}")

        # Generate image
        image_url, input_params = await ReplicateService.generate_image(
            prompt,
            user_id=user_id,
            message=None,  # Don't send status messages during generation
            operation_type="single"
        )

        if not image_url or not input_params:
            await update.message.reply_text("❌ Error generando la imagen.")
            return

        # Save prediction and send results
        await ReplicateService.save_predictions_for_images(
            [(image_url, input_params)],
            user_id,
            prompt,
            update.message  # Pass the message for sending results
        )
        logging.info(f"Successfully completed generation for user {user_id}")

    except Exception as e:
        logging.error(f"Error in generate_handler for user {user_id}: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error al generar la imagen. Por favor, intenta nuevamente."
        )
