import json
import logging


def format_generation_message(prediction_id: str, input_params: str) -> str:
    """
    Format a consistent message for image generation results.
    Shows prompt, seed, guidance_scale, prompt_strength and num_inference_steps parameters.
    """
    try:
        # Parse input_params from string
        params_dict = json.loads(input_params)

        # Filter parameters we want to show, including prompt and seed
        filtered_params = {
            "seed": params_dict.get("seed", -1),
            "prompt": params_dict.get("prompt", "No prompt provided"),
            "num_inference_steps": params_dict.get("num_inference_steps"),
            "guidance_scale": params_dict.get("guidance_scale"),
            "prompt_strength": params_dict.get("prompt_strength"),
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
