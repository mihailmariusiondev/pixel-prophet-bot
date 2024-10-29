import json
import logging


def format_generation_message(prediction_id: str, input_params: str) -> str:
    """
    Format a consistent message for image generation results showing only relevant parameters.
    Args:
        prediction_id: ID of the prediction
        input_params: JSON string of input parameters
    Returns:
        Formatted message string ready to be sent with parse_mode="Markdown"
    """
    try:
        params = json.loads(input_params)

        # Filter only relevant parameters
        relevant_params = {
            "guidance_scale": params.get("guidance_scale"),
            "prompt_strength": params.get("prompt_strength"),
            "num_inference_steps": params.get("num_inference_steps"),
            "seed": params.get("seed"),
        }

        return (
            f"🆔 `{prediction_id}`\n\n"
            f"⚙️ *Parámetros:*\n"
            f"```json\n{json.dumps(relevant_params, indent=2)}\n```\n\n"
            f"💡 `/variations {prediction_id}`"
        )

    except json.JSONDecodeError:
        logging.warning(f"Failed to parse input_params as JSON: {input_params}")
        return f"🆔 `{prediction_id}`"
