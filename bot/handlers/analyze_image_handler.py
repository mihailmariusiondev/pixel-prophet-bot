from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.database import Database

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

        # Request image description from OpenAI
        description = await chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Return ONLY the descriptive text without any headers, formatting, or meta-text. Do not include phrases like 'Prompt for Image Generation' or any section markers.

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

Format the response as a single, detailed prompt that captures all these elements in a cohesive, natural way. Focus on visual elements that are crucial for accurate image generation. Write in English and be as specific as possible while maintaining readability.""",
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            temperature=0.7,
            max_tokens=500,
        )

        if not description:
            logging.error(
                f"Failed to generate description for image from user {user_id}"
            )
            await update.message.reply_text("❌ Could not analyze the image.")
            return

        # Send the description as a new message
        await update.message.reply_text(
            f"📝 *Generated Description:*\n`{description}`", parse_mode="Markdown"
        )
        logging.info(f"Description sent to user {user_id}")

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
