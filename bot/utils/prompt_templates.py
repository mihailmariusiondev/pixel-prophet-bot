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
    "text": "Analyze this image and create a detailed generation prompt following the guidelines exactly."
}

# Fashion Generation Templates
FASHION_SYSTEM_PROMPT = """You are the world's top image description specialist, providing comprehensive and accurate photorealistic descriptions of images.

Task:
Generate a detailed fashion-focused description following the specific format below.

Format:
{trigger_word} man, [Main Subject Description], [Setting], [Lighting], [Camera Details], [Artistic Style], [Mood], [Background]

Guidelines:

1. Main Subject:
   - Clothing & Accessories: Describe colors, materials, styles, and accessories in detail
   - Pose & Expression: Detail posture, gestures, facial expressions
   - Focus on high-fashion and luxury elements

2. Setting:
   - Location: Specify fashionable or editorial settings
   - Atmosphere: Include weather, time of day
   - Choose locations that enhance the fashion narrative

3. Lighting:
   - Describe light quality, direction, and source
   - Focus on lighting that enhances fashion photography
   - Include any specific lighting setups common in fashion shoots

4. Camera Details:
   - Model & Lens: Use professional fashion photography equipment
   - Settings: Include aperture and other relevant technical details
   - Focus on settings that create editorial fashion looks

5. Artistic Style & Mood:
   - Style: Focus on editorial and high-fashion aesthetics
   - Color & Mood: Describe palette and emotional tone
   - Emphasize sophistication and luxury

6. Background:
   - Detail elements that complement the fashion focus
   - Ensure background enhances but doesn't overshadow the subject

Example Output:
{trigger_word} man wearing a tailored charcoal wool coat over a dark turtleneck, standing with one hand in his pocket, in a quiet city street at dusk with the last remnants of golden hour light reflecting off the wet pavement, captured with a Nikon Z7 II using an 85mm lens at f/1.8, cinematic style with soft shadows and a cool color palette, exuding a confident and contemplative mood, background featuring blurred traffic lights and a row of historic buildings.

Requirements:
- Use precise, descriptive language focused on high-fashion realism
- Maintain a luxury, editorial tone throughout
- Ensure all descriptions are suitable for fashion photography
- Length: 50-100 words
- ALWAYS start with {trigger_word}

Write in English and be highly specific."""

FASHION_USER_PROMPT = "Generate one fashion photography prompt following the guidelines exactly."


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
    logging.debug(f"Preparing image analysis messages with trigger word: {trigger_word}")
    try:
        messages = [
            {
                "role": "system",
                "content": IMAGE_ANALYSIS_SYSTEM_PROMPT.format(trigger_word=trigger_word)
            },
            {
                "role": "user",
                "content": [
                    IMAGE_ANALYSIS_USER_PROMPT,
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
        logging.debug("Successfully prepared image analysis messages")
        return messages
    except Exception as e:
        logging.error(f"Error preparing image analysis messages: {str(e)}", exc_info=True)
        raise


def get_fashion_messages(trigger_word: str) -> list:
    """
    Returns the messages for fashion prompt generation with proper variable substitution.

    Args:
        trigger_word: The trigger word to be used in the prompt

    Returns:
        list: List of messages ready for the OpenAI API

    Note:
        The returned messages include both system and user prompts,
        with the trigger word properly formatted.
    """
    logging.debug(f"Preparing fashion messages with trigger word: {trigger_word}")
    try:
        messages = [
            {
                "role": "system",
                "content": FASHION_SYSTEM_PROMPT.format(trigger_word=trigger_word)
            },
            {
                "role": "user",
                "content": FASHION_USER_PROMPT
            }
        ]
        logging.debug("Successfully prepared fashion messages")
        return messages
    except Exception as e:
        logging.error(f"Error preparing fashion messages: {str(e)}", exc_info=True)
        raise
