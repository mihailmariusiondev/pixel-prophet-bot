from telegram import Update
from telegram.ext import ContextTypes

async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Define the about message with bot creator information and donation link
    about_text = (
        "Bot creado por @Arkantos2374 con ❤️.\n"
        "Puedes apoyar el desarrollo del bot haciendo una donación vía [PayPal](https://paypal.me/mariusmihailion)."
    )
    # Send the about message to the user
    await update.message.reply_text(about_text, parse_mode="Markdown")
