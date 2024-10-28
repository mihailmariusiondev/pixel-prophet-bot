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
    """Handle the /variations command to generate variations of a specific prediction"""
    user_id = update.effective_user.id

    # Get user's current config
    params = db.get_user_config(user_id, ReplicateService.default_params.copy())

    # Check if a prediction ID was provided
    if context.args:
        prediction_id = context.args[0]
        try:
            # Get the specific prediction
            prediction = replicate.predictions.get(prediction_id)
            if not prediction or not prediction.input:
                await update.message.reply_text(
                    "❌ No se pudo obtener la información de la predicción especificada."
                )
                return

            # Only get the prompt from the prediction
            params["prompt"] = prediction.input.get("prompt")
            if not params["prompt"]:
                await update.message.reply_text(
                    "❌ No se pudo obtener el prompt de la predicción especificada."
                )
                return

        except Exception as e:
            logging.error(f"Error getting prediction: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ No se pudo encontrar la predicción especificada. "
                "Verifica el ID e intenta nuevamente."
            )
            return
    else:
        last_gen = db.get_last_generation(user_id)
        if not last_gen or "prompt" not in last_gen:
            await update.message.reply_text(
                "❌ No hay una generación previa. Usa /generate primero o "
                "proporciona un ID de predicción: /variations <prediction_id>"
            )
            return
        params["prompt"] = last_gen["prompt"]

    try:
        prompt = params["prompt"]
        status_message = await update.message.reply_text("⏳ Generando variaciones...")

        for i in range(3):
            variation_params = params.copy()
            variation_params["seed"] = random.randint(1, 1000000)

            result = await ReplicateService.generate_image(
                prompt,
                user_id=user_id,
                store_params=False,
                custom_params=variation_params,
            )

            if result and isinstance(result, tuple):
                image_url, prediction_id, input_params = result
                await update.message.reply_text(
                    format_generation_message(image_url, prediction_id, input_params),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    "❌ Error al generar la variación."
                )

        # Mensaje final
        await status_message.edit_text(
            "✅ Proceso completado: 3 variaciones generadas."
        )

    except Exception as e:
        logging.error(f"Error en variations_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde."
        )
