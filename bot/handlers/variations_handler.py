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

    params = db.get_user_config(user_id, ReplicateService.default_params.copy())

    if context.args:
        prediction_id = context.args[0]
        prediction_data = db.get_prediction(prediction_id)
        if not prediction_data:
            await update.message.reply_text(
                "❌ No se encontraron datos para esta predicción.\n"
                "Por favor, usa una generación más reciente o crea una nueva."
            )
            return
        prompt, input_params, _ = prediction_data
        params["prompt"] = prompt
    else:
        last_prediction = db.get_last_prediction(user_id)
        if not last_prediction:
            await update.message.reply_text(
                "❌ No hay una generación previa. Usa /generate primero o "
                "proporciona un ID de predicción: /variations <prediction_id>"
            )
            return
        params["prompt"] = last_prediction[0]

    for _ in range(3):
        await ReplicateService.generate_image(
            params["prompt"], user_id=user_id, message=update.message
        )
