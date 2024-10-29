import json
import logging

def format_generation_message(prediction_id: str, input_params: str) -> str:
    """
    Format a consistent message for image generation results.
    Args:
        prediction_id: ID of the prediction
        input_params: JSON string or dict of input parameters
    Returns:
        Formatted message string ready to be sent with parse_mode="Markdown"
    """
    try:
        # Handle input_params whether it's a string or dict
        if isinstance(input_params, str):
            formatted_params = json.dumps(json.loads(input_params), indent=2)
        elif isinstance(input_params, dict):
            formatted_params = json.dumps(input_params, indent=2)
        else:
            logging.warning(f"Unexpected input_params type: {type(input_params)}")
            formatted_params = str(input_params)
    except json.JSONDecodeError:
        logging.warning(f"Failed to parse input_params as JSON: {input_params}")
        formatted_params = str(input_params)

    return (
        f"🖼️ *Nueva generación:*\n\n"
        f"📋 [Ver en Replicate](https://replicate.com/p/{prediction_id})\n"
        f"🆔 ID: `{prediction_id}`\n\n"
        f"⚙️ *Parámetros:*\n"
        f"```json\n{formatted_params}\n```\n\n"
        f"💡 Usa `/variations {prediction_id}` para generar variaciones"
    )
