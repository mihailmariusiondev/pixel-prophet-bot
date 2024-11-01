import logging


def format_generation_message(prompt: str) -> str:
    """
    Format a consistent message for image generation results.
    Shows only the prompt used for generation.
    """
    try:
        return f"🖼️ *Nueva generación:*\n\n" f"📝 Prompt: `{prompt[:100]}...`"
    except Exception as e:
        logging.warning(f"Failed to format message: {e}")
        return "❌ Error formatting message"
