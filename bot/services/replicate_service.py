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
                input_params = await db.get_user_config(user_id, ReplicateService.default_params.copy())
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

            # Generate image
            output = await replicate.async_run(
                input_params["model_endpoint"],
                input=input_params,
            )

            if not output:
                if status_message:
                    await status_message.edit_text("❌ Error en la generación de imagen")
                return None, None

            # Clean up status message if exists
            if status_message:
                await status_message.delete()

            return output[0], input_params  # Return both URL and params used

        except Exception as e:
            logging.error(f"Error generating image: {e}")
            if status_message:
                await status_message.edit_text("❌ Error inesperado")
            return None, None

    @staticmethod
    async def save_predictions_for_images(image_urls_and_params: list, user_id: int, prompt: str, message=None):
        """
        Fetches prediction details for a list of generated images and saves them to database.
        Args:
            image_urls_and_params: List of tuples (image_url, input_params) from generation
            user_id: Telegram user ID
            prompt: Original prompt used for generation
            message: Optional telegram message for sending results
        """
        try:
            predictions_page = replicate.predictions.list()
            if predictions_page.results:
                # Match predictions with our generated images
                for prediction in predictions_page.results[:len(image_urls_and_params)]:
                    for image_url, params in image_urls_and_params:
                        if prediction.output and prediction.output[0] == image_url:
                            try:
                                await db.save_prediction(
                                    prediction_id=prediction.id,
                                    user_id=user_id,
                                    prompt=prompt,
                                    input_params=json.dumps(params),
                                    output_url=image_url
                                )
                                # Send complete info to user if message provided
                                if message:
                                    await message.reply_text(
                                        format_generation_message(prediction.id, json.dumps(params)),
                                        parse_mode="Markdown",
                                    )
                                    # Send the actual image
                                    await message.reply_photo(
                                        photo=image_url,
                                        caption="🖼️ Imagen generada"
                                    )
                                logging.info(f"Saved prediction {prediction.id} for image {image_url}")
                            except Exception as e:
                                logging.error(f"Error saving prediction: {e}")
        except Exception as e:
            logging.error(f"Error fetching/saving predictions: {e}")
