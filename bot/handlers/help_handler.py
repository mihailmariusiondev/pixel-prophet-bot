from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..utils.decorators import require_configured
from ..services.prompt_styles.manager import style_manager
from ..services.replicate_service import ReplicateService
from ..handlers.config_handler import ALLOWED_PARAMS


@require_configured
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /help command.
    Shows simplified usage information and commands.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Help command received - User: {user_id} ({username})")

    # Main commands section
    commands_help = (
        "🤖 *Formatos válidos:*\n\n"
        "• `/generate [número] [prompt]`\n"
        "  Ej: `/generate 4 retrato en un café iluminado`\n\n"
        "• `/generate [número] styles=estilo1,estilo2`\n"
        "  Ej: `/generate 3 styles=cinematic,professional`\n\n"
        "• `/generate [número]` (estilo aleatorio)\n"
        "  Ej: `/generate 5`\n\n"
        "• `/generate styles=estilo` (1 imagen)\n"
        "  Ej: `/generate styles=urban`\n\n"
    )

    # Styles section
    styles_help = (
        "🎨 *Estilos disponibles:*\n"
        "`professional, casual, cinematic, urban, minimalist, vintage, influencer, socialads`\n\n"
        "• Separa con comas los estilos que quieras usar\n"
        "• Total imágenes = número × estilos válidos\n"
        "• `random` selecciona estilo aleatorio\n\n"
    )

    # Parameters section
    params_help = (
        "⚙️ *Parámetros clave:*\n"
        "• `trigger_word`: Palabra clave para prompts\n"
        "• `model_endpoint`: Endpoint del modelo\n"
        "• `gender`: Género para generación (male/female)\n\n"
    )

    # Important notes
    important_notes = (
        "💡 *Notas importantes:*\n"
        "• Máximo 50 imágenes por comando\n"
        "• Números mayores a 50 se limitan automáticamente\n"
        "• Estilos inválidos se ignoran\n"
        "• Usa solo comas para separar estilos\n"
        "• El orden de los parámetros es importante\n"
    )

    full_help = f"{commands_help}{styles_help}{params_help}{important_notes}"

    await update.message.reply_text(
        full_help, parse_mode="Markdown", disable_web_page_preview=True
    )
