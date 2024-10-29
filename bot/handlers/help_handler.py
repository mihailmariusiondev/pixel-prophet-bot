from telegram import Update
from telegram.ext import ContextTypes
import logging


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provides comprehensive help information about bot commands and features.
    Organizes help content into sections for better readability.

    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    chat_id = update.effective_chat.id
    logging.info(f"Help command received from user {user_id} ({username}) in chat {chat_id}")

    try:
        logging.debug(f"Preparing help sections for user {user_id}")
        # Structure help text into sections
        help_sections = {
            "main_commands": (
                "*Comandos principales:*\n"
                "`/generate` \\- Genera una imagen a partir de tu descripción\n"
                "`/fashion` \\- Genera 3 imágenes de moda masculina\n"
                "`/variations` \\- Genera 3 variaciones de una imagen\n"
                "`/last_generation` \\- Muestra tu última generación\n"
            ),
            "other_features": (
                "*Otras funciones:*\n"
                "• Envía una imagen para analizarla y generar una similar\n"
            ),
            "configuration": (
                "*Configuración:*\n"
                "`/config` \\- Ver tu configuración actual\n"
                "`/config <param> <valor>` \\- Modifica un parámetro\n"
            ),
            "basic_commands": (
                "*Otros comandos:*\n"
                "`/start` \\- Inicia el bot\n"
                "`/about` \\- Información sobre el bot\n"
                "`/help` \\- Muestra este mensaje\n"
            ),
            "examples": (
                "*📝 Ejemplos:*\n"
                "• `/generate un gato jugando ajedrez en la luna`\n"
                "• `/variations abc123` \\(usando el ID de una generación\\)\n"
                "• `/config seed 42`\n"
            ),
            "tips": (
                "*💡 Tips:*\n"
                "• Puedes copiar el ID de cualquier generación para usar con variations\n"
                "• Si usas variations sin ID, se usará tu última generación\n"
                "• Usa config para personalizar los parámetros de generación\n"
                "• El comando fashion genera 3 imágenes de moda masculina automáticamente"
            )
        }

        # Combine all sections
        help_text = "\n\n".join([
            "*🤖 Guía de PixelProphetBot*\n",
            help_sections["main_commands"],
            help_sections["other_features"],
            help_sections["configuration"],
            help_sections["basic_commands"],
            help_sections["examples"],
            help_sections["tips"]
        ])

        logging.debug(f"Sending help message to user {user_id}")
        await update.message.reply_text(help_text, parse_mode="MarkdownV2")
        logging.info(f"Help message successfully sent to user {user_id}")

    except Exception as e:
        logging.error(
            f"Error sending help message to user {user_id} in chat {chat_id}: {str(e)}",
            exc_info=True
        )
        await update.message.reply_text(
            "❌ Error al mostrar la ayuda. Por favor, intenta nuevamente."
        )
