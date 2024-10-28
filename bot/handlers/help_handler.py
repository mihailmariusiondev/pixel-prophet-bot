from telegram import Update
from telegram.ext import ContextTypes
import logging


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provides comprehensive help information about bot commands and features.
    Uses MarkdownV2 formatting for better readability and visual organization.
    """
    user_id = update.effective_user.id
    logging.info(f"Help command received from user {user_id}")

    # Structured help text using sections for better organization:
    # - Main commands for core functionality
    # - Configuration options for customization
    # - Other commands for additional features
    # - Examples for practical usage
    # - Tips for advanced usage
    # Note: Special characters are escaped for MarkdownV2 compatibility
    help_text = (
        "*🤖 Guía de PixelProphetBot*\n\n"
        "*Comandos principales:*\n"
        "`/generate` \\- Genera una imagen a partir de tu descripción\n"
        "`/variations` \\- Genera 3 variaciones de una imagen\n"
        "`/last_generation` \\- Muestra tu última generación\n\n"
        "*Configuración:*\n"
        "`/config` \\- Ver tu configuración actual\n"
        "`/config <param> <valor>` \\- Modifica un parámetro\n\n"
        "*Otros comandos:*\n"
        "`/start` \\- Inicia el bot\n"
        "`/about` \\- Información sobre el bot\n"
        "`/help` \\- Muestra este mensaje\n\n"
        "*📝 Ejemplos:*\n"
        "• `/generate un gato jugando ajedrez en la luna`\n"
        "• `/variations abc123` \\(usando el ID de una generación\\)\n"
        "• `/config seed 42`\n\n"
        "*💡 Tips:*\n"
        "• Puedes copiar el ID de cualquier generación para usar con variations\n"
        "• Si usas variations sin ID, se usará tu última generación\n"
        "• Usa config para personalizar los parámetros de generación"
    )

    try:
        # Use MarkdownV2 parse mode for rich text formatting
        await update.message.reply_text(help_text, parse_mode="MarkdownV2")
        logging.debug(f"Help message sent to user {user_id}")
    except Exception as e:
        logging.error(
            f"Error sending help message to user {user_id}: {e}", exc_info=True
        )
