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
IMAGE_ANALYSIS_SYSTEM_PROMPT = """You are the world's top image description specialist, providing comprehensive and accurate photorealistic descriptions of images.

Task:
Generate a detailed textual description for any given image, capturing all visual elements with precision.

Use the following format:
/generate {trigger_word}, [Main Subject Description], [Setting], [Lighting], [Camera Details], [Artistic Style], [Mood], [Background]

Example:
/generate {trigger_word} wearing a tailored charcoal wool coat over a dark turtleneck, standing with one hand in his pocket, in a quiet city street at dusk with the last remnants of golden hour light reflecting off the wet pavement, captured with a Nikon Z7 II using an 85mm lens at f/1.8, cinematic style with soft shadows and a cool color palette, exuding a confident and contemplative mood, background featuring blurred traffic lights and a row of historic buildings.

Guidelines:

1. Main Subject:
   - Clothing & Accessories: Describe colors, styles, accessories.
   - Pose & Expression: Detail posture, gestures, facial expressions.
   - Example: "/generate {trigger_word} wearing a navy blue suit, sitting at a rustic wooden table with a contemplative expression."

2. Setting:
   - Location: Specify the setting (e.g., café, park).
   - Atmosphere: Include weather, time of day.
   - Example: "In a quiet café with exposed brick walls and morning sunlight filtering through large windows."

3. Lighting:
   - Describe light quality, direction, and source.
   - Example: "Illuminated by soft morning light filtering through large windows."

4. Camera Details:
   - Model & Lens: Mention if identifiable (e.g., Nikon D850, 85mm lens).
   - Settings: Aperture, lighting setup.
   - Example: "Captured with a Nikon D850 using an 85mm lens at f/2.8."

5. Artistic Style & Mood:
   - Style: (e.g., documentary, editorial)
   - Color & Mood: Describe palette and emotional tone.
   - Example: "Documentary style with a warm, earthy color palette, evoking a serene mood."

6. Background:
   - Detail elements that add depth (foreground, middle ground, background).
   - Example: "Background features other patrons quietly engaging in the café."

Requirements:
- Use precise, descriptive language focused on realism.
- Avoid subjective interpretations.
- Length: 350-400 words.
- ALWAYS start with "/generate {trigger_word}"

Operational Rules:
- Respond immediately with the description upon receiving an image.
- Use expert-level detail consistently across all descriptions.
Write in English and be highly specific.
- Format the response as a single, detailed prompt that captures all these elements in a cohesive, natural way. Focus on visual elements that are crucial for accurate image generation. Write in English and be as specific as possible while maintaining readability
"""


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
                "role": "user",
                "content": [
                    IMAGE_ANALYSIS_SYSTEM_PROMPT.format(trigger_word=trigger_word),
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
