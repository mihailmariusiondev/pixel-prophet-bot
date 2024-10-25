from telegram import Update
from telegram.ext import ContextTypes
from services import ReplicateService


async def generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Obtener el prompt del mensaje
    prompt = (
        update.message.text.split(" ", 1)[1]
        if len(update.message.text.split(" ", 1)) > 1
        else ""
    )

    if not prompt:
        await update.message.reply_text(
            "Por favor, proporciona un prompt para generar la imagen."
        )
        return

    # Enviar un mensaje de "Generando..."
    message = await update.message.reply_text(f"{prompt}\n> Generando...")

    # Generar la imagen
    image_url = await ReplicateService.generate_image(prompt)

    if image_url:
        # Editar el mensaje con la imagen generada
        await message.edit_text(f"{prompt}\n{image_url}")
    else:
        await message.edit_text(
            "Lo siento, hubo un error al generar la imagen. Por favor, intenta de nuevo más tarde."
        )
