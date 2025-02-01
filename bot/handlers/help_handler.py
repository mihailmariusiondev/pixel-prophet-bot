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
        "• `/generate [número]` - Genera múltiples imágenes con estilo aleatorio\n"
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
        "🎨 *Uso avanzado de estilos:*\n\n"
        "• Combina hasta 3 estilos con comas\n"
        "• Mezcla estilos base con modificadores:\n"
        "  `styles=professional,cinematic-light`\n"
        "• Usa `random` para selección aleatoria\n"
        "• Prioridad de estilos: el primero tiene mayor peso\n\n"
    )

    # Examples section
    examples = (
        "📝 *Ejemplos avanzados:*\n\n"
        "1. Un estilo por imagen:\n"
        "`/generate styles=vintage,urban` → 2 imágenes\n\n"
        "2. Múltiples imágenes por estilo:\n"
        "`/generate 6 styles=cinematic,professional` → 3 de cada\n\n"
        "3. Combinación con prompt personalizado:\n"
        "`/generate ESTEVE retrato en la ciudad styles=urban`\n\n"
        "4. Generación múltiple con prompt:\n"
        "`/generate 5 un hombre mirando al horizonte`\n\n"
        "5. Uso de estilos sin número:\n"
        "`/generate styles=professional,influencer`\n\n"
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
