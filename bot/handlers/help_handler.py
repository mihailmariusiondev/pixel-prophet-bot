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
    Shows comprehensive usage information, commands, configurations, and features.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Help command received - User: {user_id} ({username})")

    messages = []

    # 1. Introduction and Basic Commands
    messages.append(
        "🤖 *PixelProphetBot - Guía Completa*\n\n"
        "*Comandos Principales:*\n"
        "• /start - Inicia el bot y configura los parámetros esenciales\n"
        "• /help - Muestra esta guía detallada\n"
        "• /about - Información sobre el bot y su creador\n"
        "• /config - Ver o modificar la configuración\n"
        "• /generate - Genera imágenes (múltiples formatos)\n"
    )

    # 2.1 Valid and Invalid Command Combinations
    messages.append(
        "⚡ *Combinaciones del Comando /generate:*\n\n"
        "*Combinaciones Válidas:*\n"
        "• `/generate 3` - Genera 3 imágenes con estilo por defecto\n"
        "• `/generate 5 un retrato en la playa` - Genera 5 imágenes con prompt directo\n"
        "• `/generate styles=cinematic` - Una imagen con estilo cinematográfico\n"
        "• `/generate 4 styles=urban,vintage` - 4 imágenes combinando estilos\n"
        "• `/generate styles=random` - Una imagen con estilo aleatorio\n"
        "• `/generate 1 styles=random,random` - Dos imágenes con estilos aleatorios diferentes\n"
        "• `/generate 2 styles=professional,casual,cinematic,urban,minimalist,vintage,influencer,socialads,datingprofile` - 2 imágenes por cada estilo\n"
        "• `/generate styles=professional` - Una imagen con estilo profesional\n"
        "• `/generate 10 styles=urban,cinematic` - 20 imágenes (10 de cada estilo)\n"
        "• `/generate 3 styles=minimalist,vintage,urban` - 9 imágenes (3 de cada estilo)\n"
        "• `/generate 1 retrato profesional en oficina` - Una imagen con prompt directo\n\n"
        "*Combinaciones Inválidas:*\n"
        "• `/generate styles=urban un retrato` ❌ - No mezclar styles con prompt\n"
        "• `/generate 51` ❌ - Máximo 50 imágenes\n"
        "• `/generate 0` ❌ - Mínimo 1 imagen\n"
        "• `/generate styles=invalid` ❌ - Estilo no existente\n"
        "• `/generate styles=urban,` ❌ - Coma al final\n"
        "• `/generate styles=` ❌ - Styles vacío\n"
        "• `/generate styles` ❌ - Falta el = después de styles\n"
        "• `/generate ,styles=urban` ❌ - Coma al inicio\n"
        "• `/generate styles=urban,,vintage` ❌ - Comas dobles\n"
        "• `/generate styles=urban vintage` ❌ - Espacios en lugar de comas\n"
        "• `/generate -1` ❌ - Número negativo\n"
        "• `/generate 2.5` ❌ - Número decimal\n"
        "• `/generate` ❌ - Comando sin parámetros\n"
        "• `/generate styles=URBAN,vintage` ❌ - Mezcla de mayúsculas y minúsculas\n\n"
        "💡 *Tips:*\n"
        "• Los estilos inválidos en una lista se ignoran\n"
        "• El orden de los estilos no afecta el resultado\n"
        "• Puedes usar mayúsculas o minúsculas en los estilos\n"
        "• Usar todos los estilos generará 9 veces el número especificado de imágenes\n"
        "• El estilo random puede repetirse para obtener diferentes estilos aleatorios\n"
        "• El número total de imágenes es el producto del número × cantidad de estilos\n"
        "• Si no especificas número con styles=, se genera una imagen por estilo"
    )

    # 2. Generate Command Formats
    messages.append(
        "🎨 *Formatos del Comando /generate:*\n\n"
        "*1. Generación Simple:*\n"
        "• `/generate [número] [prompt]`\n"
        "Ejemplo: `/generate 4 retrato en un café`\n\n"
        "*2. Generación con Estilos:*\n"
        "• `/generate [número] styles=estilo1,estilo2`\n"
        "Ejemplo: `/generate 3 styles=cinematic,urban`\n\n"
        "*3. Generación con Estilo por Defecto:*\n"
        "• `/generate [número]`\n"
        "Ejemplo: `/generate 5`\n\n"
        "*4. Generación con Estilo Único:*\n"
        "• `/generate styles=estilo`\n"
        "Ejemplo: `/generate styles=vintage`\n\n"
        "💡 El número máximo de imágenes por comando es 50"
    )

    # 3. Available Styles with Descriptions
    messages.append(
        "🎭 *Estilos Disponibles:*\n\n"
        "• *professional* - Formal y elegante, ideal para retratos profesionales\n"
        "• *casual* - Estilo natural y auténtico tipo smartphone\n"
        "• *cinematic* - Dramático y cinematográfico, como escenas de película\n"
        "• *urban* - Fotografía urbana y callejera con energía citadina\n"
        "• *minimalist* - Limpio y minimalista con elegante simplicidad\n"
        "• *vintage* - Clásico y retro con efectos de época\n"
        "• *influencer* - Moderno y trendy para redes sociales\n"
        "• *socialads* - Optimizado para anuncios en redes sociales\n"
        "• *datingprofile* - Ideal para fotos de perfil en apps de citas\n"
        "• *random* - Selecciona un estilo al azar\n\n"
        "💡 Puedes combinar múltiples estilos usando comas"
    )

    # 4. Configuration Parameters
    config_text = "*⚙️ Parámetros de Configuración:*\n\n"
    for param, details in ALLOWED_PARAMS.items():
        config_text += f"• *{param}*\n"
        config_text += f"  - {details['description']}\n"
        if "allowed_values" in details:
            config_text += (
                f"  - Valores permitidos: {', '.join(details['allowed_values'])}\n"
            )
        elif details["type"] in ["int", "float"]:
            config_text += f"  - Rango: {details['min']} a {details['max']}\n"
        config_text += "\n"
    messages.append(config_text)

    # 5. Image Analysis Feature
    messages.append(
        "📸 *Análisis de Imágenes:*\n\n"
        "Envía una imagen al bot para:\n"
        "1. Recibir un análisis detallado de la imagen\n"
        "2. Generar una imagen similar basada en el análisis\n"
        "3. Mantener el estilo y elementos clave de la imagen original\n\n"
        "💡 Las imágenes generadas respetarán tu configuración actual"
    )

    # 6. Configuration Instructions
    messages.append(
        "🔧 *Uso de la Configuración:*\n\n"
        "*Ver configuración actual:*\n"
        "• `/config`\n\n"
        "*Modificar un parámetro:*\n"
        "• `/config [parámetro] [valor]`\n\n"
        "Ejemplos:\n"
        "• `/config gender male`\n"
        "• `/config trigger_word MARIUS`\n"
        "• `/config guidance_scale 7.5`\n\n"
        "💡 Algunos parámetros son obligatorios para usar el bot"
    )

    # 7. Important Notes and Tips (updated)
    messages.append(
        "📝 *Notas Importantes:*\n\n"
        "• El trigger_word se añade automáticamente a todos los prompts\n"
        "• Las imágenes generadas tienen una relación de aspecto 4:5\n"
        "• Los rostros siempre son visibles pero no miran directamente a la cámara\n"
        "• La calidad de la imagen depende del num_inference_steps\n"
        "• El guidance_scale controla qué tan cerca sigue el prompt\n"
        "• El prompt_strength balancea entre el prompt y la imagen original\n"
        "• Total de imágenes = número × cantidad de estilos seleccionados\n\n"
        "⚠️ *Restricciones:*\n"
        "• No se permiten escenarios sin camisa o estados de desnudez\n"
        "• No se especifica edad en los prompts\n"
        "• Se evitan contextos deportivos y de gimnasio\n"
        "• No se permiten movimientos (caminar, cruzar, etc.)\n"
        "• Los prompts son puramente descriptivos, sin títulos"
    )

    # Send each section as a separate message with better error handling
    for i, message in enumerate(messages, 1):
        try:
            await update.message.reply_text(
                message, parse_mode="Markdown", disable_web_page_preview=True
            )
        except Exception as e:
            logging.error(f"Error sending help message section {i}: {str(e)}")
            # Only send error message if it's the first failed message
            if i == 1:
                await update.message.reply_text(
                    "❌ Error al mostrar la ayuda. Por favor, intenta de nuevo más tarde o contacta al administrador."
                )
            # Continue sending remaining messages even if one fails
            continue
