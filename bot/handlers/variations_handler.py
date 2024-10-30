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
    Handle the /variations command to generate variations of a specific prediction.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Variations requested by user {user_id} ({username})")

    # Get user's current configuration
    params = db.get_user_config(user_id, ReplicateService.default_params.copy())
    logging.info(f"User {user_id} configuration fetched for variations: {params}")

    # Handle specific prediction ID if provided
    if context.args:
        prediction_id = context.args[0]
        logging.info(
            f"Generating variations for specific prediction: {prediction_id} by user {user_id}"
        )
        # Get prediction data from database
        prediction_data = db.get_prediction(prediction_id)
        if not prediction_data:
            logging.warning(
                f"No prediction data found for ID {prediction_id} requested by user {user_id}"
            )
            await update.message.reply_text(
                "❌ No se encontraron datos para esta predicción.\n"
                "Por favor, usa una generación más reciente o crea una nueva."
            )
            return
        # Extract prompt from prediction data
        prompt, input_params, _ = prediction_data
        params["prompt"] = prompt
        logging.info(f"Using prompt from prediction ID {prediction_id} for variations")
    else:
        # Get last prediction from database for this user
        last_prediction = db.get_last_prediction(user_id)
        if not last_prediction:
            logging.warning(f"No previous predictions found for user {user_id}")
            await update.message.reply_text(
                "❌ No hay una generación previa. Usa /generate primero o "
                "proporciona un ID de predicción: /variations <prediction_id>"
            )
            return
        params["prompt"] = last_prediction[0]
        logging.info(f"Using last prediction ID {last_prediction[3]} for variations")

    try:
        status_message = await update.message.reply_text("⏳ Generando variaciones...")
        logging.info(f"Sent status message for variations to user {user_id}")

        # Generate 3 variations
        for i in range(3):
            logging.info(f"Generating variation {i+1}/3 for user {user_id}")
            await ReplicateService.generate_image(
                params["prompt"], user_id=user_id, message=update.message
            )
            logging.info(f"Variation {i+1} generation initiated for user {user_id}")

        await status_message.edit_text(
            "✅ Proceso completado: 3 variaciones generadas."
        )
        logging.info(f"Completed variations generation for user {user_id}")
    except Exception as e:
        logging.error(f"Error en variations_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde."
        )
