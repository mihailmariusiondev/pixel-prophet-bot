import replicate
import asyncio
import logging
import os
from pathlib import Path
import urllib.request
import hashlib


class ReplicateService:
    @staticmethod
    def get_image_filename(url: str, prompt: str) -> str:
        """Generate a unique filename based on the URL and prompt"""
        # Create a hash of the URL to ensure uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        # Clean the prompt to use as part of filename (first 30 chars)
        clean_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30]).rstrip("_")
        return f"{clean_prompt}_{url_hash}.jpg"

    @staticmethod
    async def download_prediction(url: str, prompt: str) -> bool:
        """Download a prediction image if it doesn't already exist"""
        try:
            # Define the OneDrive path
            onedrive_path = Path(os.path.expanduser("~")) / "OneDrive" / "_Areas" / "Astria" / "Replicate"

            # Create directory if it doesn't exist
            onedrive_path.mkdir(parents=True, exist_ok=True)

            # Generate filename
            filename = ReplicateService.get_image_filename(url, prompt)
            full_path = onedrive_path / filename

            # Check if file already exists
            if full_path.exists():
                logging.info(f"Image already exists: {filename}")
                return True

            # Download the file
            logging.info(f"Downloading image to: {full_path}")
            urllib.request.urlretrieve(url, full_path)
            logging.info(f"Successfully downloaded: {filename}")
            return True

        except Exception as e:
            logging.error(f"Error downloading prediction: {e}", exc_info=True)
            return False

    @staticmethod
    async def generate_image(prompt):
        try:
            logging.info(f"Iniciando generación de imagen para prompt: {prompt}")
            output = await replicate.async_run(
                "mihailmariusiondev/marius-flux:422d4bddab17dadb069e1956009fd55d58ba6c8fd5c8d4a071241b36a7cba3c7",
                input={
                    "prompt": prompt,
                    "lora_scale": 1,
                    "num_outputs": 1,
                    "aspect_ratio": "4:5",
                    "output_format": "jpg",
                    "guidance_scale": 0,
                    "output_quality": 100,
                    "prompt_strength": 0.8,
                    "extra_lora_scale": 1,
                    "num_inference_steps": 28,
                },
            )
            logging.info(f"Respuesta de Replicate: {output}")
            if not output:
                logging.error("Replicate devolvió una respuesta vacía")
                return None

            # Download the generated image
            image_url = output[0]
            await ReplicateService.download_prediction(image_url, prompt)

            return image_url

        except replicate.exceptions.ReplicateError as e:
            logging.error(f"Error de Replicate: {e}")
            return None
        except Exception as e:
            logging.error(
                f"Error inesperado en la generación de imagen: {e}", exc_info=True
            )
            return None

    @staticmethod
    async def download_all_predictions():
        """Download all predictions that aren't already saved"""
        try:
            predictions = replicate.predictions.list()
            for prediction in predictions:
                if prediction.status == "succeeded" and prediction.output:
                    # Si la salida es una lista, toma el primer elemento
                    url = prediction.output[0] if isinstance(prediction.output, list) else prediction.output
                    prompt = prediction.input.get("prompt", "unknown_prompt")
                    await ReplicateService.download_prediction(url, prompt)

        except Exception as e:
            logging.error(f"Error downloading predictions: {e}", exc_info=True)
