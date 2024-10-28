from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import logging
from collections import deque
from ..utils.message_utils import format_generation_message

# Diccionario para almacenar las colas de prompts por usuario
user_queues = {}
# Diccionario para rastrear si un usuario está procesando actualmente
processing_status = {}


async def generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /generate command to create images from text"""
    user_id = update.effective_user.id
    logging.info(f"Generate command received from user {user_id}")

    prompt = (
        update.message.text.split(" ", 1)[1]
        if len(update.message.text.split(" ", 1)) > 1
        else ""
    )

    if not prompt:
        logging.warning(f"Empty prompt received from user {user_id}")
        await update.message.reply_text(
            "Por favor, proporciona un prompt para generar la imagen."
        )
        return

    logging.info(f"Processing generation request - User: {user_id}, Prompt: {prompt}")

    # Queue management logging
    if user_id not in user_queues:
        logging.debug(f"Initializing new queue for user {user_id}")
        user_queues[user_id] = deque()
        processing_status[user_id] = False

    message = await update.message.reply_text(f"{prompt}\n> En cola...")
    user_queues[user_id].append((prompt, message, user_id))

    queue_length = len(user_queues[user_id])
    logging.info(f"Added to queue - User: {user_id}, Queue position: {queue_length}")

    if not processing_status[user_id]:
        logging.debug(f"Starting queue processing for user {user_id}")
        await process_next_prompt(user_id)


async def process_next_prompt(user_id):
    """Procesa el siguiente prompt en la cola del usuario"""
    if not user_queues[user_id]:
        logging.debug(
            f"Queue empty for user {user_id}, setting processing status to False"
        )
        processing_status[user_id] = False
        return

    processing_status[user_id] = True
    prompt, message, user_id = user_queues[user_id].popleft()
    logging.info(f"Processing prompt for user {user_id}: {prompt}")

    try:
        await message.edit_text("⏳ Generando imagen...")
        result = await ReplicateService.generate_image(prompt, user_id=user_id)

        if result and isinstance(result, tuple):
            image_url, prediction_id, input_params = result
            await message.edit_text(
                format_generation_message(image_url, prediction_id, input_params),
                parse_mode="Markdown",
            )
        else:
            await message.edit_text(
                "❌ Error al generar la imagen. Por favor, verifica tu prompt e intenta nuevamente."
            )
    except Exception as e:
        logging.error(f"Error procesando prompt: {e}", exc_info=True)
        await message.edit_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta más tarde."
        )
    finally:
        await process_next_prompt(user_id)
