import replicate
import logging
import json
from ..utils.database import Database
import random

db = Database()


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
    async def generate_image(prompt, user_id=None):
        """
        Generates an image using the Replicate API.
        Args:
            prompt: Text description for image generation
            user_id: Optional Telegram user ID for config lookup
        Returns:
            tuple: (image_url, prediction_id, parameters_json) or None on failure
        """
        try:
            logging.info(
                f"Starting image generation - User: {user_id}, Prompt: {prompt}"
            )

            # Get user config or default params
            if user_id is not None:
                input_params = db.get_user_config(
                    user_id, ReplicateService.default_params.copy()
                )
                logging.debug(f"Using user-specific configuration for user {user_id}")
            else:
                input_params = ReplicateService.default_params.copy()
                logging.debug("Using default configuration")

            # Always randomize seed before generation
            input_params["seed"] = random.randint(1, 1000000)
            input_params["prompt"] = prompt

            logging.info("Sending request to Replicate API")
            output = await replicate.async_run(
                "mihailmariusiondev/marius-flux:422d4bddab17dadb069e1956009fd55d58ba6c8fd5c8d4a071241b36a7cba3c7",
                input=input_params,
            )

            if not output:
                logging.error("Replicate returned empty response")
                return None

            logging.info("Successfully received response from Replicate")

            # Get prediction details
            predictions_page = replicate.predictions.list()
            if predictions_page.results:
                latest_prediction = predictions_page.results[0]
                logging.info(f"Retrieved prediction ID: {latest_prediction.id}")

                # Store prediction data in database
                db.save_prediction(
                    prediction_id=latest_prediction.id,
                    user_id=user_id,
                    prompt=prompt,
                    input_params=json.dumps(input_params),
                    output_url=output[0],
                )

                return (
                    output[0],
                    latest_prediction.id,
                    json.dumps(input_params, indent=2),
                )
            else:
                logging.error("No predictions found in response")
                return None

        except replicate.exceptions.ReplicateError as e:
            logging.error(f"Replicate API error: {e}", exc_info=True)
            return None
        except Exception as e:
            logging.error(f"Unexpected error in image generation: {e}", exc_info=True)
            return None
