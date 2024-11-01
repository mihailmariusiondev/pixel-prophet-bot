import replicate
import logging
import json
from ..utils.database import db
import random
from ..utils.message_utils import format_generation_message
import asyncio


class ReplicateService:
    """
    Handles all interactions with the Replicate API for image generation.
    Provides methods for generating images, downloading predictions,
    and managing variations of existing images.
    """

    # Default parameters for image generation
    # These values have been tuned for optimal results
    default_params = {
        "seed": -1,  # Default seed value, will be randomized during generation
        "model": "dev",  # Model version
        "lora_scale": 1,  # LoRA adaptation strength
        "num_outputs": 1,  # Number of images to generate
        "aspect_ratio": "4:5",  # Standard Instagram ratio
        "output_format": "jpg",  # Compressed format for efficiency
        "guidance_scale": 0,  # How closely to follow the prompt
        "output_quality": 100,  # Maximum quality for saved images
        "prompt_strength": 0.8,  # Balance between prompt and image
        "extra_lora_scale": 1,  # Additional LoRA adjustment
        "num_inference_steps": 28,  # Balance between quality and speed
    }

    @staticmethod
    async def generate_image(
        prompt, user_id=None, message=None, operation_type="single"
    ):
        """
        Generates an image using the Replicate API.
        Returns:
            tuple: (image_url, input_params) or (None, None) on failure
        """
        try:
            # Initialize status message if needed
            status_message = None
            if message:
                status_text = {
                    "single": "⏳ Generando imagen...",
                    "variation": "⏳ Generando variación...",
                    "analysis": "⏳ Generando imagen basada en análisis...",
                }.get(operation_type, "⏳ Procesando...")
                status_message = await message.reply_text(status_text)

            # Get configuration
            if user_id is not None:
                input_params = await db.get_user_config(
                    user_id, ReplicateService.default_params.copy()
                )
            else:
                input_params = ReplicateService.default_params.copy()

            # Validate config
            trigger_word = input_params.get("trigger_word")
            model_endpoint = input_params.get("model_endpoint")
            if not trigger_word or not model_endpoint:
                if status_message:
                    await status_message.edit_text("❌ Configuración incompleta.")
                return None, None

            # Prepare generation parameters
            input_params["seed"] = random.randint(1, 1000000)
            input_params["prompt"] = prompt

            # Añadimos logs antes de la generación
            logging.info("Parámetros de entrada:")
            logging.info(json.dumps(input_params, indent=2))

            # Generate image
            logging.info("Iniciando generación con async_run...")
            prediction = await replicate.async_run(
                input_params["model_endpoint"],
                input=input_params,
            )

            logging.info(f"Prediction object: {prediction}")
            # Captura el ID de la predicción
            prediction_id = prediction["id"]
            logging.info(f"ID de la predicción: {prediction_id}")

            # Añadimos log del output completo
            logging.info("Output completo de replicate:")
            logging.info(json.dumps(prediction, indent=2))

            if not prediction:
                if status_message:
                    await status_message.edit_text(
                        "❌ Error en la generación de imagen"
                    )
                return None, None

            # Llamar a la API para obtener toda la información de la predicción
            logging.info(
                f"Obteniendo información completa de la predicción {prediction_id}"
            )
            prediction_info = await replicate.predictions.get(prediction_id)

            # Guardar la información completa de la predicción en la base de datos
            await db.save_prediction(
                prediction_id=prediction_info["id"],
                user_id=user_id,
                prompt=prompt,
                input_params=json.dumps(prediction_info["input"]),
                output_url=prediction_info["output"],
            )

            # Clean up status message if exists
            if status_message:
                await status_message.delete()

            return (
                prediction_info["output"],
                input_params,
            )  # Return both URL and params used

        except Exception as e:
            logging.error(f"Error generating image: {e}")
            if status_message:
                await status_message.edit_text("❌ Error inesperado")
            return None, None
