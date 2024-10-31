"""
Collection of prompt templates used across the application.
Each template is organized by its specific use case and follows a consistent
system prompt + user prompt structure.

The templates are designed to:
1. Generate consistent, high-quality prompts
2. Maintain specific formatting requirements
3. Include necessary trigger words
4. Follow best practices for each use case
"""

import logging

# Image Analysis Templates
IMAGE_ANALYSIS_SYSTEM_PROMPT = """You are a world-class prompt engineer specializing in creating detailed, precise image descriptions for AI image generation. Your expertise lies in analyzing images and creating prompts that capture every significant detail.
Your analysis must cover ALL of the following aspects:
1. Main Subject:
- Precise description of the subject(s)
- Pose, expression, and positioning
- Clothing and accessories in detail
- Age range and distinguishing features
2. Composition:
- Camera angle and perspective
- Framing and positioning
- Distance from subject
- Rule of thirds or other techniques
3. Environment/Setting:
- Location details
- Background elements
- Time of day
- Weather conditions
- Architectural or natural elements
4. Lighting:
- Main light source and direction
- Shadow characteristics
- Lighting style
- Highlights and contrast
5. Color Palette:
- Dominant colors
- Color relationships
- Tonal range
- Color temperature
6. Technical Details:
- Image style
- Lens characteristics
- Depth of field
- Texture qualities
7. Mood and Atmosphere:
- Overall emotional tone
- Atmospheric effects
- Environmental mood
Format: Single, coherent paragraph without sections.
Style: Technical but natural description.
ALL prompts MUST start with '{trigger_word}'
Write in English and be as specific as possible."""

IMAGE_ANALYSIS_USER_PROMPT = {
    "type": "text",
    "text": "Analyze this image and create a detailed generation prompt following the guidelines exactly.",
}


def get_image_analysis_messages(trigger_word: str, image_url: str) -> list:
    """
    Returns the messages for image analysis with proper variable substitution.

    Args:
        trigger_word: The trigger word to be used in the prompt
        image_url: URL of the image to be analyzed

    Returns:
        list: List of messages ready for the OpenAI API

    Note:
        The returned messages include both system and user prompts,
        with the trigger word properly formatted and image URL embedded.
    """
    logging.debug(
        f"Preparing image analysis messages with trigger word: {trigger_word}"
    )
    try:
        messages = [
            {
                "role": "system",
                "content": IMAGE_ANALYSIS_SYSTEM_PROMPT.format(
                    trigger_word=trigger_word
                ),
            },
            {
                "role": "user",
                "content": [
                    IMAGE_ANALYSIS_USER_PROMPT,
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ]
        logging.debug("Successfully prepared image analysis messages")
        return messages
    except Exception as e:
        logging.error(
            f"Error preparing image analysis messages: {str(e)}", exc_info=True
        )
        raise
