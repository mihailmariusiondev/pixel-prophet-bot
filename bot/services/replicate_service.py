import os
import replicate

class ReplicateService:
    @staticmethod
    async def generate_image(prompt):
        try:
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={"prompt": prompt}
            )
            return output[0] if output else None
        except Exception as e:
            print(f"Error en la generación de imagen: {e}")
            return None
