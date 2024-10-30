from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..utils.database import Database
from ..utils.message_utils import format_generation_message

db = Database()


async def last_generation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /last_generation command to show details of the user's last generation.
    Retrieves all information from local database.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    chat_id = update.effective_chat.id

    logging.info(
        f"Last generation requested by user {user_id} ({username}) in chat {chat_id}"
    )

    try:
        # Get last prediction from database
        last_prediction = db.get_last_prediction(user_id)
        logging.info(f"Retrieved last prediction for user {user_id}: {last_prediction}")

        if not last_prediction:
            logging.warning(f"No previous predictions found for user {user_id}")
            await update.message.reply_text(
                "❌ No hay generaciones previas. Usa /generate para crear una nueva imagen."
            )
            return

        # Unpack all 4 values
        prompt, input_params, output_url, prediction_id = last_prediction
        logging.info(f"Last prediction ID for user {user_id}: {prediction_id}")

        # Send the details message
        await update.message.reply_text(
            format_generation_message(prediction_id, input_params),
            parse_mode="Markdown",
        )
        logging.info(f"Sent generation details to user {user_id}")

        # Then send the image
        await update.message.reply_photo(
            photo=output_url, caption="🖼️ Tu última generación"
        )
        logging.info(f"Successfully sent last generation image to user {user_id}")

    except Exception as e:
        logging.error(
            f"Error in last_generation_handler for user {user_id}: {e}", exc_info=True
        )
        await update.message.reply_text(
            "❌ Ocurrió un error al recuperar la última generación."
        )
