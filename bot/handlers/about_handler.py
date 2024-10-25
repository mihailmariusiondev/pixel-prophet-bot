from telegram import Update
from telegram.ext import ContextTypes

async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "PixelProphetBot: genera imágenes de texto\n"
        "Creador: @Arkantos2374\n"
        "Dona: paypal.me/mariusmihailion"
    )
    await update.message.reply_text(about_text)
