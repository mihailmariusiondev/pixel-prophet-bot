import replicate
import logging
import os
from pathlib import Path
import urllib.request
from datetime import datetime
import json
from ..utils.config import user_configs


class ReplicateService:
    # Parámetros predeterminados
    default_params = {
        "seed": 42,
        "model": "dev",
        "lora_scale": 1,
        "num_outputs": 1,
        "aspect_ratio": "4:5",
        "output_format": "jpg",
        "guidance_scale": 0,
        "output_quality": 100,
        "prompt_strength": 0.8,
        "extra_lora_scale": 1,
        "num_inference_steps": 28,
    }

    @staticmethod
    def get_image_filename(prediction) -> str:
        """Generate a filename based on creation date, ID and prompt"""
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
        """Download a prediction image if it doesn't already exist"""
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
    async def generate_image(prompt, user_id=None):
        try:
            logging.info(f"Iniciando generación de imagen para prompt: {prompt}")

            # Obtener configuración del usuario
            if user_id is not None and user_id in user_configs:
                input_params = user_configs[user_id].copy()
                logging.info(f"Usando configuración personalizada para usuario {user_id}: {input_params}")
            else:
                input_params = ReplicateService.default_params.copy()
                logging.info("Usando configuración predeterminada")

            input_params["prompt"] = prompt

            output = await replicate.async_run(
                "mihailmariusiondev/marius-flux:422d4bddab17dadb069e1956009fd55d58ba6c8fd5c8d4a071241b36a7cba3c7",
                input=input_params,
            )

            logging.info(f"Respuesta de Replicate: {output}")
            if not output:
                logging.error("Replicate devolvió una respuesta vacía")
                return None

            # Get the prediction object for the generated image
            predictions_page = replicate.predictions.list()
            if predictions_page.results:
                latest_prediction = predictions_page.results[0]
                # Download the generated image
                await ReplicateService.download_prediction(latest_prediction)

                # Return tuple with image URL, prediction ID, and input parameters
                return (
                    output[0],  # image URL
                    latest_prediction.id,  # prediction ID
                    json.dumps(input_params, indent=2),  # formatted JSON string
                )
            else:
                logging.error("No predictions found")
                return None

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
