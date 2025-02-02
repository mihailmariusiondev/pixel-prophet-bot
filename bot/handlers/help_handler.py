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
        "• `/generate [número] [prompt]` - Genera múltiples imágenes del mismo prompt\n"
        "• `/generate [número]` - Genera imágenes con estilo aleatorio\n"
        "• `/generate [número] styles=estilo1,estilo2` - Combina estilos para generación\n"
        "• `/generate styles=estilo` - Genera con estilo específico sin número\n"
        "• `/generate [número] [prompt]` - Genera múltiples variaciones de un prompt\n"
        "• `/generate [prompt] styles=estilo` - Combina prompt con estilo específico\n\n"
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
        "🎨 *Uso de estilos:*\n\n"
        "• El número especificado se aplica a CADA estilo\n"
        "• Total de imágenes = número × cantidad de estilos\n"
        "• Máximo 3 estilos por comando\n"
        "• Estilos inválidos son ignorados\n"
        "• Usa `random` para selección aleatoria de estilo\n"
        "• Los nombres de estilos son insensibles a mayúsculas\n\n"
    )

    # Examples section
    examples = (
        "📝 *Ejemplos avanzados:*\n\n"
        "1. Un estilo con múltiples imágenes:\n"
        "`/generate 3 styles=professional` → 3 imágenes\n\n"
        "2. Dos estilos con imágenes por estilo:\n"
        "`/generate 2 styles=cinematic,vintage` → 4 imágenes (2 de cada)\n\n"
        "3. Tres estilos con una imagen cada uno:\n"
        "`/generate 1 styles=urban,minimalist,influencer` → 3 imágenes\n\n"
        "4. Generación múltiple con prompt directo:\n"
        "`/generate 4 retrato en un café iluminado` → 4 imágenes iguales\n\n"
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

    # Edge cases section
    edge_cases = (
        "⚠️ *Casos especiales:*\n\n"
        "• Mayúsculas: `styles=PROFESSIONAL` se convierte a minúscula\n"
        "• Estilos inválidos: se ignoran silenciosamente\n"
        "• Números mayores a 50: se limitan automáticamente\n"
        "• Mezcla de formatos: `/generate 3 prompt styles=estilo` es inválido\n"
        "• Sin espacios: `styles= estilo` puede causar errores\n"
    )

    # Combine all sections
    full_help = f"{commands_help}{config_help}{styles_help}{examples}{tips}{edge_cases}"

    # Send help message
    await update.message.reply_text(
        full_help, parse_mode="Markdown", disable_web_page_preview=True
    )
