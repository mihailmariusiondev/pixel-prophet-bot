import logging


async def format_generation_message(
    prompt: str, message=None, image_url=None, prediction_id=None
) -> str:
    """
    Format and optionally send a message with image for generation results.
    """
    try:
        base_text = "📝 Prompt: `"
        hint_text = ""

        if len(prompt) > 4093:
            formatted_prompt = prompt[:4090] + "...`"
        else:
            formatted_prompt = prompt + "`"

        formatted_text = base_text + formatted_prompt + hint_text

        # If message and image_url are provided, send to chat
        if message and image_url:
            await message.reply_photo(photo=image_url)
            await message.reply_text(formatted_text, parse_mode="Markdown")
            return None

        return formatted_text
    except Exception as e:
        logging.warning(f"Failed to format message: {e}")
        return "❌ Error formatting message"
