import logging
from telegram import Update
from telegram.ext import CallbackContext

async def error_handler(update: object, context: CallbackContext) -> None:
    # Log the error with full traceback
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

    # Log additional context about the error
    if isinstance(update, Update):
        if update.effective_chat:
            logging.error(f"Error occurred in chat_id: {update.effective_chat.id}")
        if update.effective_user:
            logging.error(f"Error occurred for user_id: {update.effective_user.id}")
        if update.effective_message:
            logging.error(f"Error occurred in message_id: {update.effective_message.message_id}")

    # If the update is available and has an effective message, send an error message to the user
    if isinstance(update, Update) and update.effective_message:
        error_message = "Ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente más tarde."
        try:
            # Attempt to send an error message to the user
            await update.effective_message.reply_text(error_message)
            logging.info(f"Error message sent to user in chat_id: {update.effective_chat.id}")
        except Exception as e:
            logging.error(f"Failed to send error message to user: {e}")
