from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
from ..utils.database import Database
import logging
from ..utils.decorators import require_configured

db = Database()


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
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Variations requested - User: {user_id} ({username})")

    try:
        # Get base configuration
        params = db.get_user_config(user_id, ReplicateService.default_params.copy())
        logging.info(f"Retrieved user config - User: {user_id}")

        # Handle specific prediction ID if provided
        if context.args:
            prediction_id = context.args[0]
            logging.info(
                f"Variation requested for specific prediction: {prediction_id} - User: {user_id}"
            )

            prediction_data = db.get_prediction(prediction_id)
            if not prediction_data:
                logging.warning(
                    f"Prediction not found: {prediction_id} - User: {user_id}"
                )
                await update.message.reply_text(
                    "❌ No se encontraron datos para esta predicción.\n"
                    "Por favor, usa una generación más reciente o crea una nueva."
                )
                return
            prompt, input_params, _ = prediction_data
            logging.info(
                f"Retrieved prediction data successfully - User: {user_id}, ID: {prediction_id}"
            )
        else:
            # Use last prediction if no ID provided
            last_prediction = db.get_last_prediction(user_id)
            if not last_prediction:
                logging.warning(f"No previous predictions found - User: {user_id}")
                await update.message.reply_text(
                    "❌ No hay una generación previa. Usa /generate primero o "
                    "proporciona un ID de predicción: /variations <prediction_id>"
                )
                return
            prompt = last_prediction[0]
            logging.info(f"Using last prediction for variations - User: {user_id}")

        # Generate variations
        for i in range(3):
            logging.info(f"Generating variation {i+1}/3 - User: {user_id}")
            try:
                await ReplicateService.generate_image(
                    prompt,
                    user_id=user_id,
                    message=update.message,
                    operation_type="variation",
                )
                logging.info(
                    f"Successfully generated variation {i+1} - User: {user_id}"
                )
            except Exception as e:
                logging.error(
                    f"Failed to generate variation {i+1} - User: {user_id}, Error: {str(e)}"
                )
                # Continue with next variation even if one fails
                continue

    except Exception as e:
        logging.error(f"Error in variations_handler - User: {user_id}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error al generar las variaciones."
        )
