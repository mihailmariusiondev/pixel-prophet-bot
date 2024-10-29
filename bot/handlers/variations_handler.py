from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
from ..utils.database import Database
import logging
import random
import replicate
from ..utils.message_utils import format_generation_message

db = Database()


async def variations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /variations command to generate variations of a specific prediction.
    Can work with either a provided prediction ID or the user's last generation.

    Args:
        update: Telegram update object
        context: Bot context containing command arguments
    """
    user_id = update.effective_user.id
    logging.info(f"Variations requested by user {user_id}")

    # Get user's current configuration
    params = db.get_user_config(user_id, ReplicateService.default_params.copy())
    logging.debug(f"Retrieved user config for {user_id}: {params}")

    # Handle specific prediction ID if provided
    if context.args:
        prediction_id = context.args[0]
        logging.info(f"Generating variations for specific prediction: {prediction_id}")

        # Attempt to retrieve prediction data
        prediction_data = await ReplicateService.get_prediction_data(prediction_id)
        if not prediction_data:
            logging.warning(f"No data found for prediction {prediction_id}")
            await update.message.reply_text(
                "❌ No se encontraron datos para esta predicción.\n"
                "Los datos pueden haber sido eliminados de Replicate.\n"
                "Por favor, usa una generación más reciente o crea una nueva."
            )
            return

        # Extract prompt from prediction data
        params["prompt"] = prediction_data.get("prompt") or prediction_data.input.get("prompt")
        logging.debug(f"Retrieved prompt for variation: {params['prompt']}")

        if not params["prompt"]:
            logging.error(f"Could not extract prompt from prediction {prediction_id}")
            await update.message.reply_text(
                "❌ No se pudo obtener el prompt de la predicción."
            )
            return
    else:
        # Get last prediction from Replicate
        predictions_page = replicate.predictions.list()
        if not predictions_page.results:
            await update.message.reply_text(
                "❌ No hay una generación previa. Usa /generate primero o "
                "proporciona un ID de predicción: /variations <prediction_id>"
            )
            return
        latest_prediction = predictions_page.results[0]
        params["prompt"] = latest_prediction.input.get("prompt")

    try:
        prompt = params["prompt"]
        logging.info(f"Starting variation generation for prompt: {prompt}")
        status_message = await update.message.reply_text("⏳ Generando variaciones...")

        for i in range(3):
            variation_params = params.copy()
            variation_params["seed"] = random.randint(1, 1000000)
            logging.debug(
                f"Generating variation {i+1}/3 with seed: {variation_params['seed']}"
            )

            result = await ReplicateService.generate_image(
                prompt,
                user_id=user_id,
                custom_params=variation_params,
            )
            if result and isinstance(result, tuple):
                image_url, prediction_id, input_params = result
                # First send the details message
                await update.message.reply_text(
                    format_generation_message(prediction_id, input_params),
                    parse_mode="Markdown"
                )
                # Then send the image
                await update.message.reply_photo(
                    photo=image_url,
                    caption="🖼️ Variación generada"
                )
            else:
                await update.message.reply_text("❌ Error al generar la variación.")
        # Mensaje final
        await status_message.edit_text(
            "✅ Proceso completado: 3 variaciones generadas."
        )
    except Exception as e:
        logging.error(f"Error en variations_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde."
        )
