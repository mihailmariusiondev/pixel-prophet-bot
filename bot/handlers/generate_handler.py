from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import logging
from collections import deque


# Diccionario para almacenar las colas de prompts por usuario
user_queues = {}
# Diccionario para rastrear si un usuario está procesando actualmente
processing_status = {}


async def generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    user_id = update.effective_user.id

    # Inicializar la cola del usuario si no existe
    if user_id not in user_queues:
        user_queues[user_id] = deque()
        processing_status[user_id] = False

    # Crear un mensaje de estado
    message = await update.message.reply_text(f"{prompt}\n> En cola...")

    # Agregar el prompt y mensaje a la cola
    user_queues[user_id].append((prompt, message))

    # Si no hay procesamiento activo, iniciar uno
    if not processing_status[user_id]:
        await process_next_prompt(user_id)


async def process_next_prompt(user_id):
    """Procesa el siguiente prompt en la cola del usuario"""
    if not user_queues[user_id]:
        processing_status[user_id] = False
        return

    processing_status[user_id] = True
    prompt, message = user_queues[user_id].popleft()

    try:
        # Actualizar mensaje a "Generando..."
        await message.edit_text(f"{prompt}\n> Generando...")

        # Generar la imagen
        image_url = await ReplicateService.generate_image(prompt)

        if image_url:
            await message.edit_text(f"{prompt}\n{image_url}")
        else:
            await message.edit_text(
                "Lo siento, hubo un error al generar la imagen. "
                "Por favor, verifica que tu prompt sea apropiado y no contenga contenido prohibido."
            )
    except Exception as e:
        logging.error(f"Error procesando prompt: {e}", exc_info=True)
        await message.edit_text(
            "Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde."
        )
    finally:
        # Procesar el siguiente prompt en la cola
        await process_next_prompt(user_id)
