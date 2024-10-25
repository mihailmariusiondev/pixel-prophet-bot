from telegram import Update
from telegram.ext import ContextTypes


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "¡Bienvenido a PixelProphetBot! 🎨✨\n\n"
        "Soy un bot que genera imágenes únicas basadas en tus descripciones de texto.\n\n"
        "Para comenzar, simplemente usa el comando /generate seguido de tu descripción.\n"
        "Por ejemplo: /generate un gato jugando ajedrez en la luna\n\n"
        "¡Diviértete explorando tu creatividad!"
    )
    await update.message.reply_text(welcome_text)
