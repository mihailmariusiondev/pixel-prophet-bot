import replicate
import logging
from ..utils.database import db
import random
from ..utils.message_utils import format_generation_message


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
        "num_outputs": 1,  # Default to single image generation
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
            # Initialize status message if needed - solo si NO es una variación
            status_message = None
            if message and operation_type != "variation":
                # Eliminamos los mensajes individuales por imagen
                if status_message:
                    await status_message.delete()

            # Get configuration - simplified
            input_params = (
                await db.get_user_config(
                    user_id, ReplicateService.default_params.copy()
                )
                if user_id is not None
                else ReplicateService.default_params.copy()
            )

            # Validate config
            if not input_params.get("trigger_word") or not input_params.get(
                "model_endpoint"
            ):
                if status_message:
                    await status_message.edit_text("❌ Configuración incompleta.")
                return None, None

            # Prepare generation parameters
            input_params["seed"] = random.randint(1, 1000000)
            input_params["prompt"] = prompt

            # Generate image
            logging.info("Iniciando generación con async_run...")
            output = await replicate.async_run(
                input_params["model_endpoint"],
                input=input_params,
            )

            if not output or not output[0]:
                raise Exception("No se generó ninguna imagen")

            # Save prediction and get prediction_id
            prediction_id = await db.save_prediction(
                user_id=user_id, prompt=prompt, output_url=output[0]
            )

            # Si la generación fue exitosa y tenemos un mensaje
            if output and output[0] and message:
                await format_generation_message(
                    prompt, message, output[0], prediction_id
                )

            return output[0], input_params

        except Exception as e:
            logging.error(f"Error generating image: {e}")
            if status_message:
                await status_message.edit_text("❌ Error inesperado")
            return None, None
