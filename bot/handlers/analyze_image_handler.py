from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.message_utils import format_generation_message


async def analyze_image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming images to analyze and generate similar ones"""
    try:
        user_id = update.effective_user.id
        logging.info(f"Image analysis requested by user {user_id}")

        # Check if there's an image
        if not update.message.photo:
            await update.message.reply_text("❌ Please send an image to analyze.")
            return

        # Get the image with best resolution
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_url = file.file_path

        # Send status message
        status_message = await update.message.reply_text("🔍 Analyzing image...")

        # Using the generic chat_completion with vision message format
        description = await chat_completion(
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Create a detailed image generation prompt based on this image. Focus on describing the main subject, composition, lighting, mood, and style. Keep it concise but descriptive. Write in English and focus on visual elements that would be important for image generation.",
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            }],
            temperature=0.7,
            max_tokens=300
        )

        if not description:
            await status_message.edit_text("❌ Could not analyze the image.")
            return

        # Update status message while generating
        await status_message.edit_text("⏳ Generating image...")

        # Generate new image based on description
        result = await ReplicateService.generate_image(description, user_id=user_id)

        if result and isinstance(result, tuple):
            image_url, prediction_id, input_params = result
            # Send only the generation result, like /generate command
            await update.message.reply_text(
                format_generation_message(image_url, prediction_id, input_params),
                parse_mode="Markdown",
            )
        else:
            await status_message.edit_text("❌ Error generating the image.")

    except Exception as e:
        logging.error(f"Error in analyze_image_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ An error occurred while processing the image."
        )
