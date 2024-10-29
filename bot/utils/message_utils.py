import json
import logging


def format_generation_message(prediction_id: str, input_params: str) -> str:
    """
    Format a consistent message for image generation results.
    Only shows guidance_scale, prompt_strength and num_inference_steps parameters.
    """
    try:
        # Parse input_params from string
        params_dict = json.loads(input_params)
        
        # Filter only the parameters we want to show
        filtered_params = {
            k: v
            for k, v in params_dict.items()
            if k in ["guidance_scale", "prompt_strength", "num_inference_steps"]
        }

        formatted_params = json.dumps(filtered_params, indent=2)

        return (
            f"🖼️ *Nueva generación:*\n\n"
            f"📋 [Ver en Replicate](https://replicate.com/p/{prediction_id})\n"
            f"🆔 ID: `{prediction_id}`\n\n"
            f"⚙️ *Parámetros:*\n"
            f"```json\n{formatted_params}\n```\n\n"
            f"💡 Usa `/variations {prediction_id}` para generar variaciones"
        )
    except json.JSONDecodeError:
        logging.warning(f"Failed to parse input_params as JSON: {input_params}")
        return "❌ Error formatting message"
