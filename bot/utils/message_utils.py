def format_generation_message(
    image_url: str, prediction_id: str, input_params: str
) -> str:
    """
    Format a consistent message for all image generation results.

    Args:
        image_url: URL of the generated image
        prediction_id: ID of the prediction
        input_params: JSON string of input parameters

    Returns:
        Formatted message string ready to be sent with parse_mode="Markdown"
    """
    return (
        f"🖼️ *Nueva generación:*\n\n"
        f"🔗 [Ver imagen]({image_url})\n"
        f"📋 [Ver en Replicate](https://replicate.com/p/{prediction_id})\n"
        f"🆔 ID: `{prediction_id}`\n\n"
        f"⚙️ *Parámetros:*\n"
        f"```json\n{input_params}\n```\n\n"
        f"💡 Usa `/variations {prediction_id}` para generar variaciones"
    )
