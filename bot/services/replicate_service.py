import replicate
import logging
import os
from pathlib import Path
import urllib.request
from datetime import datetime
import json
from ..utils import Database

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
        "seed": 42,  # For reproducibility
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
    def get_image_filename(prediction) -> str:
        """
        Generates a standardized filename for saved images.
        Format: date_id_prompt.jpg
        Handles special characters and length limitations.
        """
        try:
            # Convertir el string de fecha a objeto datetime
            # El formato de Replicate es: "2024-03-20T14:30:22.907244Z"
            created_at = datetime.strptime(
                prediction.created_at.split(".")[0], "%Y-%m-%dT%H:%M:%S"
            )

            # Formatear la fecha
            date_str = created_at.strftime("%Y-%m-%d_%H%M%S")

            # Limpiar el prompt (primeros 30 caracteres)
            prompt = prediction.input.get("prompt", "unknown_prompt")
            clean_prompt = "".join(
                c if c.isalnum() else "_" for c in prompt[:30]
            ).rstrip("_")

            # Crear nombre: fecha_id_prompt.jpg
            return f"{date_str}_{prediction.id}_{clean_prompt}.jpg"

        except Exception as e:
            logging.error(f"Error generating filename: {e}", exc_info=True)
            # Nombre de respaldo si algo falla
            return f"unknown_date_{prediction.id}.jpg"

    @staticmethod
    async def download_prediction(prediction) -> bool:
        """
        Downloads and saves prediction images to OneDrive.
        Implements idempotency to avoid duplicate downloads.

        Args:
            prediction: Replicate prediction object

        Returns:
            bool: True if download successful or file exists
        """
        try:
            # Define the OneDrive path
            onedrive_path = (
                Path(os.path.expanduser("~"))
                / "OneDrive"
                / "_Areas"
                / "Astria"
                / "Replicate"
            )

            # Create directory if it doesn't exist
            onedrive_path.mkdir(parents=True, exist_ok=True)

            # Generate filename
            filename = ReplicateService.get_image_filename(prediction)
            full_path = onedrive_path / filename

            # Check if file already exists
            if full_path.exists():
                logging.info(f"Image already exists: {filename}")
                return True

            # Get the URL from prediction output
            url = (
                prediction.output[0]
                if isinstance(prediction.output, list)
                else prediction.output
            )

            # Download the file
            logging.info(f"Downloading image to: {full_path}")
            urllib.request.urlretrieve(url, full_path)
            logging.info(f"Successfully downloaded: {filename}")
            return True

        except Exception as e:
            logging.error(f"Error downloading prediction: {e}", exc_info=True)
            return False

    @staticmethod
    async def generate_image(prompt, user_id=None, custom_params=None):
        """
        Generates an image using the Replicate API.
        Supports custom parameters and user-specific configurations.

        Args:
            prompt: Text description for image generation
            user_id: Optional Telegram user ID for config lookup
            custom_params: Optional override for generation parameters

        Returns:
            tuple: (image_url, prediction_id, parameters_json) or None on failure
        """
        try:
            logging.info(
                f"Starting image generation - User: {user_id}, Prompt: {prompt}"
            )

            if custom_params:
                input_params = custom_params
                logging.debug(f"Using custom parameters: {input_params}")
            else:
                if user_id is not None:
                    input_params = db.get_user_config(
                        user_id, ReplicateService.default_params.copy()
                    )
                    logging.debug(f"Using user config for {user_id}: {input_params}")
                else:
                    input_params = ReplicateService.default_params.copy()
                    logging.debug("Using default configuration")

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

                # Download the generated image
                logging.debug("Initiating image download")
                await ReplicateService.download_prediction(latest_prediction)

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

    @staticmethod
    async def download_all_predictions():
        """Download all predictions from all pages"""
        try:
            count = 0
            all_predictions = []

            # Obtener primera página
            current_page = replicate.predictions.list()

            # Recopilar todas las predicciones de todas las páginas
            while True:
                # Añadir predicciones de la página actual
                all_predictions.extend(current_page.results)

                # Si no hay más páginas, salir del bucle
                if not current_page.next:
                    break

                # Obtener siguiente página
                current_page = replicate.predictions.list(current_page.next)

            # Ordenar todas las predicciones por fecha
            sorted_predictions = sorted(
                all_predictions,
                key=lambda x: x.created_at,
                reverse=True,  # True = más reciente primero
            )

            # Procesar predicciones ordenadas
            for prediction in sorted_predictions:
                if prediction.status == "succeeded" and prediction.output:
                    if await ReplicateService.download_prediction(prediction):
                        count += 1
                        logging.info(
                            f"Downloaded {count} of {len(sorted_predictions)} predictions"
                        )

            logging.info(f"Successfully downloaded {count} predictions from all pages")
            return count

        except Exception as e:
            logging.error(f"Error downloading predictions: {e}", exc_info=True)
            raise
