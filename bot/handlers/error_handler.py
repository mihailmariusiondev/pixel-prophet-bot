import logging
from telegram import Update
from telegram.ext import CallbackContext

async def error_handler(update: object, context: CallbackContext) -> None:
    """
    Global error handler for the bot. Catches and logs all errors that occur during bot operation.
    Provides detailed logging while sending user-friendly error messages.

    Args:
        update: Telegram update object (might be None in some error cases)
        context: Callback context containing error information
    """
    # Log the full error with traceback for debugging
    logging.error("Exception while handling an update:", exc_info=context.error)

    # Extract and log detailed context about where the error occurred
    error_context = {
        'update_id': getattr(update, 'update_id', 'N/A'),
        'error': str(context.error),
        'error_type': type(context.error).__name__
    }

    if isinstance(update, Update):
        if update.effective_chat:
            error_context['chat_id'] = update.effective_chat.id
            logging.error(f"Error occurred in chat_id: {update.effective_chat.id}")

        if update.effective_user:
            error_context['user_id'] = update.effective_user.id
            error_context['username'] = update.effective_user.username
            logging.error(f"Error occurred for user_id: {update.effective_user.id}")

        if update.effective_message:
            error_context['message_id'] = update.effective_message.message_id
            error_context['message_text'] = update.effective_message.text
            logging.error(f"Error occurred in message_id: {update.effective_message.message_id}")

    # Log the complete error context
    logging.error(f"Full error context: {error_context}")

    # Attempt to notify user about the error
    if isinstance(update, Update) and update.effective_message:
        error_message = "Ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente más tarde."
        try:
            # Send user-friendly error message
            await update.effective_message.reply_text(error_message)
            logging.info(f"Error message sent to user in chat_id: {update.effective_chat.id}")
        except Exception as e:
            logging.error(f"Failed to send error message to user: {e}", exc_info=True)
