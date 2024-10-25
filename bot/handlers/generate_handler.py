from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import asyncio
import logging


# Diccionario para almacenar las tareas en proceso
active_tasks = {}


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

    # Enviar mensaje de "Generando..."
    message = await update.message.reply_text(f"{prompt}\n> Generando...")

    # Crear la tarea y almacenarla
    user_id = update.effective_user.id
    if user_id not in active_tasks:
        active_tasks[user_id] = []

    # Crear y almacenar la nueva tarea
    task = asyncio.create_task(ReplicateService.generate_image(prompt))
    active_tasks[user_id].append((task, message, prompt))

    # Configurar callback para cuando la tarea termine
    task.add_done_callback(
        lambda t: asyncio.create_task(
            handle_task_completion(t, message, prompt, user_id)
        )
    )


async def handle_task_completion(task, message, prompt, user_id):
    try:
        image_url = await task
        if image_url:
            logging.info(f"Imagen generada exitosamente: {image_url}")
            await message.edit_text(f"{prompt}\n{image_url}")
        else:
            logging.error(f"No se pudo generar la imagen para el prompt: {prompt}")
            await message.edit_text(
                "Lo siento, hubo un error al generar la imagen. "
                "Por favor, verifica que tu prompt sea apropiado y no contenga contenido prohibido."
            )
    except asyncio.CancelledError:
        logging.warning(f"Tarea cancelada para el prompt: {prompt}")
        await message.edit_text("La generación de imagen fue cancelada.")
    except Exception as e:
        logging.error(f"Error en handle_task_completion: {e}", exc_info=True)
        await message.edit_text(
            "Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde."
        )
    finally:
        # Limpiar la tarea completada
        active_tasks[user_id] = [(t, m, p) for t, m, p in active_tasks[user_id] if t != task]
        if not active_tasks[user_id]:
            del active_tasks[user_id]
