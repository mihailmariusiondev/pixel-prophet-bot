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
    """
    Handle the /generate command to create images from text.
    Implements a queue system to manage multiple requests from the same user.

    Args:
        update: Telegram update object containing message and prompt
        context: Bot context for maintaining state
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Generate command received from user {user_id} ({username})")

    # Extract prompt from message, skipping the command itself
    prompt = (
        update.message.text.split(" ", 1)[1]
        if len(update.message.text.split(" ", 1)) > 1
        else ""
    )

    # Validate prompt presence
    if not prompt:
        logging.warning(f"Empty prompt received from user {user_id}")
        await update.message.reply_text(
            "Por favor, proporciona un prompt para generar la imagen."
        )
        return

    logging.info(f"Processing generation request - User: {user_id}, Prompt: {prompt[:100]}...")

    # Initialize queue for new users
    if user_id not in user_queues:
        logging.debug(f"Initializing new queue for user {user_id}")
        user_queues[user_id] = deque()
        processing_status[user_id] = False

    # Add request to user's queue
    message = await update.message.reply_text(f"{prompt}\n> En cola...")
    user_queues[user_id].append((prompt, message, user_id))

    queue_length = len(user_queues[user_id])
    logging.info(f"Request queued - User: {user_id}, Queue position: {queue_length}, Queue size: {len(user_queues[user_id])}")

    # Start processing if not already running
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
    logging.info(f"Processing prompt for user {user_id}: {prompt[:100]}...")

    try:
        logging.debug(f"Updating status message for user {user_id}")
        await message.edit_text("⏳ Generando imagen...")

        result = await ReplicateService.generate_image(prompt, user_id=user_id)
        if result and isinstance(result, tuple):
            image_url, prediction_id, input_params = result
            logging.info(f"Successfully generated image for user {user_id} - Prediction ID: {prediction_id}")

            # Send messages
            await message.reply_text(
                format_generation_message(prediction_id, input_params),
                parse_mode="Markdown"
            )
            await message.reply_photo(
                photo=image_url,
                caption="🖼️ Imagen generada"
            )
            logging.debug(f"Successfully sent generation results to user {user_id}")
        else:
            logging.error(f"Failed to generate image for user {user_id} - Invalid result format")
            await message.edit_text(
                "❌ Error al generar la imagen. Por favor, verifica tu prompt e intenta nuevamente."
            )
    except Exception as e:
        logging.error(f"Error processing prompt for user {user_id}: {str(e)}", exc_info=True)
        await message.edit_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta más tarde."
        )
    finally:
        logging.debug(f"Processing next prompt in queue for user {user_id}")
        await process_next_prompt(user_id)
