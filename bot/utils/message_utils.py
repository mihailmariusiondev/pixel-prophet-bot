import logging


def format_generation_message(prompt: str) -> str:
    """
    Format a consistent message for image generation results.
    Shows only the prompt used for generation.
    Handles Telegram's 4096 character limit.
    """
    try:
        base_text = "🖼️ *Nueva generación:*\n\n📝 Prompt: `"
        max_prompt_length = 4096 - len(base_text) - 1  # -1 for the closing backtick

        if len(prompt) > max_prompt_length:
            formatted_prompt = prompt[:max_prompt_length-3] + "...`"
        else:
            formatted_prompt = prompt + "`"

        return base_text + formatted_prompt

    except Exception as e:
        logging.warning(f"Failed to format message: {e}")
        return "❌ Error formatting message"
