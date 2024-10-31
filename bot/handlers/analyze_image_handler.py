from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.database import Database

# Analysis prompt templates
ANALYSIS_PROMPT = """Return ONLY the descriptive text without any headers, formatting, or meta-text. Do not include phrases like 'Prompt for Image Generation' or any section markers.

Analyze this image and create an extremely detailed generation prompt. Include ALL of the following aspects:

Key elements to include:
- ALL prompts MUST start with '{trigger_word}'

1. Main Subject:
- Precise description of the subject(s)
- Pose, expression, and positioning
- Clothing and accessories in detail
- Age range and distinguishing features

2. Composition:
- Camera angle and perspective
- Framing and positioning
- Distance from subject (close-up, medium, full shot)
- Rule of thirds or other compositional techniques

3. Environment/Setting:
- Location details
- Background elements
- Time of day
- Weather conditions (if applicable)
- Architectural or natural elements

4. Lighting:
- Main light source and direction
- Shadow characteristics
- Lighting style (natural, studio, dramatic, etc.)
- Highlights and contrast details

5. Color Palette:
- Dominant colors
- Color relationships
- Tonal range
- Color temperature

6. Technical Details:
- Image style (photorealistic, cinematic, editorial)
- Lens characteristics (focal length effect)
- Depth of field
- Texture and material qualities

7. Mood and Atmosphere:
- Overall emotional tone
- Atmospheric effects
- Environmental mood indicators

Format the response as a single, detailed prompt that captures all these elements in a cohesive, natural way. Focus on visual elements that are crucial for accurate image generation. Write in English and be as specific as possible while maintaining readability."""

SPECIALIST_PROMPT = """Return ONLY the descriptive text without any headers, formatting, or meta-text. Do not include phrases like 'Prompt for Image Generation' or any section markers.

Analyze this image and create an extremely detailed generation prompt. Include ALL of the following aspects:

Use the following format:
- {trigger_word}, [Main Subject Description], [Setting], [Lighting], [Camera Details], [Artistic Style], [Mood], [Background]
- Example:
{trigger_word} wearing a tailored charcoal wool coat over a dark turtleneck, standing with one hand in his pocket, in a quiet city street at dusk with the last remnants of golden hour light reflecting off the wet pavement, captured with a Nikon Z7 II using an 85mm lens at f/1.8, cinematic style with soft shadows and a cool color palette, exuding a confident and contemplative mood, background featuring blurred traffic lights and a row of historic buildings.

Guidelines:

1. Main Subject:
   - Clothing & Accessories: Describe colors, styles, accessories.
   - Pose & Expression: Detail posture, gestures, facial expressions.
   - Example: "{trigger_word} wearing a navy blue suit, sitting at a rustic wooden table with a contemplative expression."

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

Format the response as a single, detailed prompt that captures all these elements in a cohesive, natural way. Focus on visual elements that are crucial for accurate image generation. Write in English and be as specific as possible while maintaining readability."""

db = Database()


async def analyze_image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming images to analyze and generate similar ones.
    Uses OpenAI's vision model to create a description, then generates a similar image.

    Args:
        update: Telegram update containing the image
        context: Bot context for maintaining state
    """
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        logging.info(f"Image analysis requested by user {user_id} ({username})")

        # Validate image presence
        if not update.message.photo:
            logging.warning(f"User {user_id} sent message without image")
            await update.message.reply_text("❌ Please send an image to analyze.")
            return

        # Get user configuration
        config = db.get_user_config(user_id, ReplicateService.default_params.copy())
        trigger_word = config.get("trigger_word")

        # Get highest resolution image from message
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_url = file.file_path
        logging.info(f"Retrieved image URL for user {user_id}: {image_url}")

        # Send initial status message
        status_message = await update.message.reply_text("🔍 Analyzing image...")
        logging.info(
            f"Starting image analysis for user {user_id} - File ID: {photo.file_id}"
        )

        # Request image description from OpenAI
        description = await chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": ANALYSIS_PROMPT.format(trigger_word=trigger_word),
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            temperature=1,
            max_tokens=8192,
        )

        if not description:
            logging.error(
                f"Failed to generate description for image from user {user_id}"
            )
            await status_message.edit_text("❌ Could not analyze the image.")
            return

        # Send the description as a new message
        await update.message.reply_text(
            f"📝 *Generated Description:*\n`{description}`", parse_mode="Markdown"
        )
        logging.info(f"Description sent to user {user_id}")

        # Update status for image generation
        await status_message.edit_text("⏳ Generando imagen...")
        logging.info(f"Starting image generation based on analysis for user {user_id}")
        logging.info(f"Generated description for user {user_id}: {description}...")

        # Generate new image and send results
        await ReplicateService.generate_image(
            description, user_id=user_id, message=update.message
        )
        logging.info(f"Image generation initiated for user {user_id}")
    except Exception as e:
        logging.error(
            f"Error in analyze_image_handler for user {user_id}: {str(e)}",
            exc_info=True,
        )
        await update.message.reply_text(
            "❌ An error occurred while processing the image."
        )
