import replicate
import asyncio


class ReplicateService:
    @staticmethod
    async def generate_image(prompt):
        try:
            # Usamos asyncio.to_thread para ejecutar la llamada a Replicate de forma asíncrona
            output = await asyncio.to_thread(
                replicate.run,
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
            return output[0] if output else None
        except Exception as e:
            print(f"Error en la generación de imagen: {e}")
            return None
