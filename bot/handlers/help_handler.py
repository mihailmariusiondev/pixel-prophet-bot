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
    Shows detailed usage information, commands, and configuration options.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Help command received - User: {user_id} ({username})")

    # Dividir el mensaje en partes más pequeñas para evitar problemas con el formato
    messages = []

    # Comandos principales
    messages.append(
        "🤖 *Comandos Principales:*\n"
        "• /start - Inicia el bot y muestra mensaje de bienvenida\n"
        "• /help - Muestra este mensaje de ayuda\n"
        "• /about - Información sobre el bot y su creador\n"
        "• /config - Ver o modificar la configuración\n"
        "• /generate - Genera imágenes (ver formatos abajo)\n"
    )

    # Formatos de generación
    messages.append(
        "📸 *Formatos de /generate:*\n\n"
        "*1. Prompt Directo:*\n"
        "• /generate [número] [prompt]\n"
        "Ejemplo: /generate 4 retrato en un café\n\n"
        "*2. Estilos Específicos:*\n"
        "• /generate [número] styles=estilo1,estilo2\n"
        "Ejemplo: /generate 3 styles=cinematic,urban\n\n"
        "*3. Estilo por Defecto:*\n"
        "• /generate [número]\n"
        "Ejemplo: /generate 5\n\n"
        "*4. Un Solo Estilo:*\n"
        "• /generate styles=estilo\n"
        "Ejemplo: /generate styles=vintage"
    )

    # Estilos disponibles
    messages.append(
        "🎨 *Estilos Disponibles:*\n"
        "• professional - Formal y elegante\n"
        "• casual - Estilo casual y auténtico\n"
        "• cinematic - Estilo cinematográfico\n"
        "• urban - Fotografía urbana\n"
        "• minimalist - Minimalista y limpio\n"
        "• vintage - Clásico y retro\n"
        "• influencer - Estilo redes sociales\n"
        "• socialads - Anuncios sociales\n"
        "• datingprofile - Perfil de citas\n"
        "• random - Estilo aleatorio"
    )

    # Configuración
    messages.append(
        "⚙️ *Configuración:*\n"
        "• Ver configuración actual: /config\n"
        "• Modificar parámetro: /config [parámetro] [valor]\n\n"
        "*Parámetros Principales:*\n"
        "• trigger_word - Palabra clave para prompts\n"
        "• model_endpoint - Endpoint del modelo\n"
        "• gender - Género (male/female)\n"
        "• guidance_scale - Control de prompt (0-10)\n"
        "• prompt_strength - Balance prompt/imagen (0-1)\n"
        "• num_inference_steps - Calidad/velocidad (1-50)"
    )

    # Notas importantes
    messages.append(
        "💡 *Notas Importantes:*\n"
        "• Máximo 50 imágenes por comando\n"
        "• Total imágenes = número × estilos seleccionados\n"
        "• No mezclar prompt directo con styles=\n"
        "• Configurar trigger_word y model_endpoint antes de usar\n"
        "• Los estilos inválidos se ignoran\n"
        "• El trigger_word se añade automáticamente"
    )

    # Enviar cada sección como un mensaje separado
    for message in messages:
        try:
            await update.message.reply_text(
                message, parse_mode="Markdown", disable_web_page_preview=True
            )
        except Exception as e:
            logging.error(f"Error sending help message: {str(e)}")
            await update.message.reply_text(
                "❌ Error al mostrar la ayuda. Por favor, contacta al administrador."
            )
            break
