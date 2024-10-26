from telegram import Update
from telegram.ext import ContextTypes


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Aquí tienes una guía rápida de cómo usar PixelProphetBot:\n\n"
        "/start - Inicia el bot y muestra el mensaje de bienvenida\n"
        "/generate [descripción] - Genera una imagen basada en tu descripción\n"
        "/download - Descarga todas las imágenes generadas a OneDrive\n"
        "/about - Muestra información sobre el bot y su creador\n"
        "/help - Muestra este mensaje de ayuda\n\n"
        "Para generar una imagen, simplemente usa /generate seguido de tu descripción.\n"
        "Ejemplo: /generate un paisaje futurista con rascacielos flotantes\n\n"
        "¡Experimenta con diferentes descripciones y deja volar tu imaginación!"
    )
    await update.message.reply_text(help_text)
