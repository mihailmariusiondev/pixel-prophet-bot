from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.prompt_templates import get_image_analysis_messages
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
        logging.info(f"Image analysis requested - User: {user_id} ({username})")

        # Validate image presence
        if not update.message.photo:
            logging.warning(f"No image provided - User: {user_id}")
            await update.message.reply_text("❌ Please send an image to analyze.")
            return

        # Get user configuration
        config = db.get_user_config(user_id, ReplicateService.default_params.copy())
        trigger_word = config.get("trigger_word")

        # Get highest resolution image from message
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_url = file.file_path
        logging.info(f"Image URL retrieved - User: {user_id}, File ID: {photo.file_id}")

        # Send initial analysis status
        status_message = await update.message.reply_text("🔍 Analyzing image...")
        logging.info(f"Started image analysis - User: {user_id}")

        # Request image description from OpenAI
        description = await chat_completion(
            messages=get_image_analysis_messages(trigger_word, image_url),
            temperature=0.7,
            max_tokens=500,
        )

        # Handle failed description generation
        if not description:
            logging.error(f"Failed to generate description - User: {user_id}")
            await status_message.edit_text("❌ Could not analyze the image.")
            return

        # Clean up analysis status message
        await status_message.delete()

        # Send the description to user
        await update.message.reply_text(
            f"📝 *Generated Description:*\n`{description}`", parse_mode="Markdown"
        )
        logging.info(f"Description sent to user - User: {user_id}")

        # Generate image based on description
        await ReplicateService.generate_image(
            description,
            user_id=user_id,
            message=update.message,
            operation_type="analysis",
        )
        logging.info(f"Image generation initiated - User: {user_id}")

    except Exception as e:
        logging.error(
            f"Error in analyze_image_handler - User: {user_id}", exc_info=True
        )
        await update.message.reply_text(
            "❌ An error occurred while processing the image."
        )
