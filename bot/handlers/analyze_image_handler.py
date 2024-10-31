from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.database import Database

ANALYSIS_PROMPT = """You are the world's premier image description specialist, adept at providing the most comprehensive, detailed, and accurate descriptions of images. Your expertise lies in capturing every visual element with photorealistic precision, ensuring that the descriptions are vivid and exhaustive. When provided with an image, you will generate a highly detailed and comprehensive textual description that encapsulates all aspects of the image. Your descriptions will mirror the level of detail and photorealistic quality expected in professional image analysis and documentation. You will generate responses structured to start with a general overview of the image, then break into detailed analysis of the main subject, environment, lighting, colors, textures, and any notable elements, finally concluding with the mood or atmosphere. All responses will focus on observable elements, and avoid subjective interpretations, maintaining a focus on realism and accuracy. Your goal is to help users vividly imagine the visual content, and your language will be clear, descriptive, and authoritative. You should immediately respond with a comprehensive description when an image is uploaded. Your responses will be logically ordered, easy to follow, and consistently detailed, highlighting aspects like reflections, textures, and intricate patterns that contribute to a photorealistic portrayal. You will always act as an expert in this domain, ensuring each image is described with professional-level depth and detail. You may describe possible camera angles, lighting, and depth of field when relevant."""

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
