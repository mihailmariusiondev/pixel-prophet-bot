from telegram import Update
from telegram.ext import ContextTypes
import logging


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.info(f"Help command received from user {user_id}")

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
        await update.message.reply_text(help_text, parse_mode="MarkdownV2")
        logging.debug(f"Help message sent to user {user_id}")
    except Exception as e:
        logging.error(
            f"Error sending help message to user {user_id}: {e}", exc_info=True
        )
