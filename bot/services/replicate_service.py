import replicate
import logging


class ReplicateService:
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
            return output[0]
        except replicate.exceptions.ReplicateError as e:
            logging.error(f"Error de Replicate: {e}")
            return None
        except Exception as e:
            logging.error(
                f"Error inesperado en la generación de imagen: {e}", exc_info=True
            )
            return None
