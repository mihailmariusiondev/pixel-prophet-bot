import logging


async def format_generation_message(prompt: str, message=None, image_url=None) -> str:
    """
    Format and optionally send a message with image for generation results.
    If message and image_url are provided, sends the message to chat.
    """
    try:
        base_text = "📝 Prompt: `"
        max_prompt_length = 4096 - len(base_text) - 1  # -1 for the closing backtick
        if len(prompt) > max_prompt_length:
            formatted_prompt = prompt[:max_prompt_length-3] + "...`"
        else:
            formatted_prompt = prompt + "`"

        formatted_text = base_text + formatted_prompt

        # If message and image_url are provided, send to chat
        if message and image_url:
            await message.reply_photo(
                photo=image_url,
                caption=formatted_text,
                parse_mode="Markdown"
            )
            return None

        return formatted_text
    except Exception as e:
        logging.warning(f"Failed to format message: {e}")
        return "❌ Error formatting message"
