from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.message_utils import format_generation_message


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
        logging.info(f"Image analysis requested by user {user_id}")

        # Validate image presence
        if not update.message.photo:
            logging.warning(f"User {user_id} sent message without image")
            await update.message.reply_text("❌ Please send an image to analyze.")
            return

        # Get highest resolution image from message
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_url = file.file_path
        logging.debug(f"Retrieved image URL: {image_url}")

        # Send initial status message
        status_message = await update.message.reply_text("🔍 Analyzing image...")
        logging.info(f"Starting image analysis for user {user_id}")

        # Request image description from OpenAI
        description = await chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Create a detailed image generation prompt based on this image. Focus on describing the main subject, composition, lighting, mood, and style. Keep it concise but descriptive. Write in English and focus on visual elements that would be important for image generation.",
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            temperature=0.7,
            max_tokens=300,
        )

        if not description:
            logging.error(
                f"Failed to generate description for image from user {user_id}"
            )
            await status_message.edit_text("❌ Could not analyze the image.")
            return

        logging.info(
            f"Generated description: {description[:100]}..."
        )  # Log first 100 chars

        # Update status while generating new image
        await status_message.edit_text("⏳ Generating image...")
        logging.info(f"Starting image generation based on analysis for user {user_id}")

        # Generate new image using the description
        result = await ReplicateService.generate_image(description, user_id=user_id)
        if result and isinstance(result, tuple):
            image_url, prediction_id, input_params = result
            logging.info(f"Successfully generated image with ID: {prediction_id}")
            await update.message.reply_text(
                format_generation_message(image_url, prediction_id, input_params),
                parse_mode="Markdown",
            )
        else:
            logging.error(f"Image generation failed for user {user_id}")
            await status_message.edit_text("❌ Error generating the image.")

    except Exception as e:
        logging.error(f"Error in analyze_image_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ An error occurred while processing the image."
        )
