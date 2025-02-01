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
    Shows detailed information about bot usage and available commands.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Help command received - User: {user_id} ({username})")

    # Main commands section
    commands_help = (
        "🤖 *Comandos disponibles:*\n\n"
        "• `/generate [prompt]` - Genera imágenes a partir de un prompt\n"
        "• `/generate [número]` - Genera múltiples imágenes con prompts aleatorios\n"
        "• `/generate [número] styles=estilo1,estilo2` - Genera imágenes con estilos específicos\n"
        "• `/config` - Muestra la configuración actual\n"
        "• `/config [param] [valor]` - Modifica un parámetro de configuración\n"
        "• `/help` - Muestra este mensaje de ayuda\n\n"
    )

    # Configuration parameters section
    config_help = "⚙️ *Parámetros de configuración:*\n\n"
    for param, details in ALLOWED_PARAMS.items():
        config_help += f"• `{param}`: {details['description']}\n"
        if details["type"] == "str" and "allowed_values" in details:
            config_help += (
                f"  Valores permitidos: {', '.join(details['allowed_values'])}\n"
            )
        elif details["type"] == "str":
            config_help += f"  Longitud: {details['min_length']}-{details['max_length']} caracteres\n"
        else:
            config_help += f"  Rango: {details['min']}-{details['max']}\n"
        config_help += "\n"

    # Styles section
    available_styles = style_manager.get_available_styles()
    styles_help = (
        "🎨 *Estilos disponibles:*\n\n"
        f"• {', '.join(f'`{style}`' for style in available_styles if style != 'random')}\n"
        "• `random` - Selecciona un estilo aleatorio\n\n"
    )

    # Examples section
    examples = (
        "📝 *Ejemplos:*\n\n"
        "1. Generar una imagen con un prompt:\n"
        "`/generate ESTEVE un hombre sentado en un café, mirando pensativamente por la ventana`\n\n"
        "2. Generar 3 imágenes con prompts aleatorios:\n"
        "`/generate 3`\n\n"
        "3. Generar 4 imágenes con estilos específicos:\n"
        "`/generate 4 styles=vintage,urban`\n\n"
        "4. Ajustar la calidad de generación:\n"
        "`/config num_inference_steps 40`\n\n"
        "5. Generar con estilos específicos sin número:\n"
        "`/generate styles=vintage,cinematic`\n\n"
    )

    # Tips section
    tips = (
        "💡 *Tips:*\n\n"
        "• Los prompts deben ser detallados y descriptivos\n"
        "• Especifica siempre la dirección de la mirada del sujeto\n"
        "• Evita movimiento o poses dinámicas\n"
        "• No especifiques edad ni características físicas específicas\n"
        "• Puedes combinar múltiples estilos en una sola generación\n"
    )

    # Combine all sections
    full_help = f"{commands_help}{config_help}{styles_help}{examples}{tips}"

    # Send help message
    await update.message.reply_text(
        full_help, parse_mode="Markdown", disable_web_page_preview=True
    )
