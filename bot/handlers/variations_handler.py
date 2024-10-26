from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
from ..utils.config import last_generations  # Importar desde config
import logging
import random
import json

async def variations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /variations command to generate variations of the last prompt"""
    user_id = update.effective_user.id

    # Verificar si existe una generación previa
    if not last_generations or user_id not in last_generations:
        await update.message.reply_text(
            "❌ No hay una generación previa. Primero usa /generate para crear una imagen."
        )
        return

    try:
        # Obtener los parámetros de la última generación
        params = last_generations[user_id].copy()
        prompt = params["prompt"]
        shortened_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt

        # Mensaje inicial
        status_message = await update.message.reply_text(
            f"🎨 Generando 3 variaciones para:\n{shortened_prompt}\n\n> Iniciando..."
        )

        # Generar 3 variaciones con seeds aleatorios
        for i in range(3):
            variation_params = params.copy()
            new_seed = random.randint(1, 1000000)
            variation_params["seed"] = new_seed

            # Actualizar mensaje de estado
            await status_message.edit_text(
                f"🎨 Generando variación {i+1}/3 para:\n{shortened_prompt}\n\n"
                f"> Seed: {new_seed}"
            )

            result = await ReplicateService.generate_image(
                prompt,
                user_id=user_id,
                store_params=False,
                custom_params=variation_params
            )

            if result and isinstance(result, tuple):
                image_url, prediction_id, input_params = result
                # Enviar cada variación inmediatamente
                variation_message = (
                    f"🎨 Variación {i+1}/3:\n"
                    f"Prompt: {shortened_prompt}\n\n"
                    f"🔗 Image: {image_url}\n"
                    f"📋 Prediction: https://replicate.com/p/{prediction_id}\n\n"
                    f"⚙️ Parameters:\n"
                    f"```json\n{input_params}\n```"
                )
                await update.message.reply_text(variation_message, parse_mode="Markdown")
            else:
                await update.message.reply_text(
                    f"❌ Error generando la variación {i+1}/3. Continuando con la siguiente..."
                )

        # Mensaje final
        await status_message.edit_text(
            f"✅ Proceso completado: 3 variaciones generadas para:\n{shortened_prompt}"
        )

    except Exception as e:
        logging.error(f"Error en variations_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde."
        )
