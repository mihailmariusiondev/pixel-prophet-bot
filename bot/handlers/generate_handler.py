from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import logging
from collections import deque
from ..utils.message_utils import format_generation_message

# Global queues to manage multiple requests per user
# Using dictionaries to isolate each user's queue and processing state
user_queues = {}        # Maps user_id to their request queue
processing_status = {}  # Tracks if a user has active processing


async def generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles image generation requests from users.
    Implements a queue system to manage multiple requests per user.
    Extracts prompt from message and validates input before processing.
    """
    user_id = update.effective_user.id
    logging.info(f"Generate command received from user {user_id}")

    # Extract prompt from message, splitting on first space after command
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

    # Initialize queue system for new users
    if user_id not in user_queues:
        logging.debug(f"Initializing new queue for user {user_id}")
        user_queues[user_id] = deque()
        processing_status[user_id] = False

    # Add request to user's queue
    message = await update.message.reply_text(f"{prompt}\n> En cola...")
    user_queues[user_id].append((prompt, message, user_id))
    queue_length = len(user_queues[user_id])
    logging.info(f"Added to queue - User: {user_id}, Queue position: {queue_length}")

    # Start processing if no active generation for this user
    if not processing_status[user_id]:
        logging.debug(f"Starting queue processing for user {user_id}")
        await process_next_prompt(user_id)


async def process_next_prompt(user_id):
    """
    Processes queued prompts for a specific user.
    Implements FIFO queue processing with automatic continuation.
    Handles generation errors and updates message status accordingly.

    Args:
        user_id: The Telegram user ID whose queue to process
    """
    # Check if queue is empty
    if not user_queues[user_id]:
        logging.debug(f"Queue empty for user {user_id}, setting processing status to False")
        processing_status[user_id] = False
        return

    # Mark as processing and get next prompt
    processing_status[user_id] = True
    prompt, message, user_id = user_queues[user_id].popleft()
    logging.info(f"Processing prompt for user {user_id}: {prompt}")

    try:
        # Update message to show generation status
        await message.edit_text("⏳ Generando imagen...")
        result = await ReplicateService.generate_image(prompt, user_id=user_id)

        if result and isinstance(result, tuple):
            # Unpack and format successful generation result
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
        # Continue processing queue regardless of success/failure
        await process_next_prompt(user_id)
