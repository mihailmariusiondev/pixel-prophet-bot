from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.database import Database

ANALYSIS_PROMPT = """You are a world-class prompt engineer specializing in creating exceptional, highly detailed prompts for AI text-to-image tools like Stable Diffusion, Midjourney, and Leonardo AI. Your expertise lies in crafting prompts that result in photorealistic, hyper-realistic images that are nearly indistinguishable from reality.

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

Important instructions:
- ALL your prompts must start with /generate {trigger_word}, [Main Subject Description], [Setting], [Lighting], [Camera Details], [Artistic Style], [Mood], [Background]
- Confident Attitude: Subjects should exude confidence through posture, gaze, masculinity and interaction with their environment.
- CRITICAL: Detailed Physical Qualities: Highlight an athletic build subtly
- CRITICAL: The subject's face must be visible but NOT looking directly at the camera. Describe a specific direction or point of focus for the subject's gaze (e.g., "gazing thoughtfully at a distant horizon," "eyes focused on an object in his hands," "looking slightly to the side with a pensive expression")."""

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

        if not description or "I'm sorry" in description:
            logging.error(
                f"Failed to generate description for image from user {user_id} - OpenAI declined to assist"
            )
            await status_message.edit_text(
                "❌ No se pudo analizar la imagen debido a las políticas de contenido."
            )
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
