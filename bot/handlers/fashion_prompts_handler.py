from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.message_utils import format_generation_message


async def fashion_prompts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate multiple fashion prompts and create images"""
    user_id = update.effective_user.id
    logging.info(f"Fashion prompts generation requested by user {user_id}")

    try:
        status_message = await update.message.reply_text(
            "🎭 Generating fashion prompts..."
        )
        prompts = []

        system_prompt = """You are a world-class prompt engineer specializing in creating exceptional, highly detailed prompts for AI text-to-image tools. Your expertise lies in crafting prompts that result in photorealistic, hyper-realistic images.

Create a single prompt with these key elements:
- MUST start with 'MARIUS'
- Subject must exude confidence through posture and environment interaction
- Include subtle athletic build description
- CRITICAL: Explicitly describe gaze direction (NOT at camera, but face must be visible)

Follow these restrictions:
- No shirtless/undressed scenarios
- No age specifications
- No sports/gym contexts
- Focus on professional/casual/formal settings
- No movement descriptions
- Elegant but not luxury-focused
- Pure description, no titles
- ABSOLUTELY ESSENTIAL: In every prompt, explicitly state the subject's gaze direction, ensuring it is not towards the camera while keeping the face visible and engaging.

Return ONLY the prompt text, no additional formatting or explanations. The prompt must be a single, coherent sentence."""

        # Generate 3 separate prompts
        for i in range(3):
            prompt = await chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": "Generate one fashion prompt following the guidelines exactly.",
                    },
                ],
                temperature=0.7,
            )

            if prompt:
                # Clean up the prompt - remove any extra whitespace or line breaks
                clean_prompt = " ".join(prompt.strip().split())
                if clean_prompt.startswith("MARIUS"):
                    prompts.append(clean_prompt)

        if not prompts:
            await status_message.edit_text("❌ Error generating prompts.")
            return

        # Generate images for each prompt
        await status_message.edit_text("🎨 Generating images from prompts...")

        for prompt in prompts:
            result = await ReplicateService.generate_image(prompt, user_id=user_id)
            if result and isinstance(result, tuple):
                image_url, prediction_id, input_params = result
                await update.message.reply_text(
                    f"*Original Prompt:*\n`{prompt}`\n\n"
                    + format_generation_message(image_url, prediction_id, input_params),
                    parse_mode="Markdown",
                )

        await status_message.edit_text("✅ Fashion prompt generation completed!")

    except Exception as e:
        logging.error(f"Error in fashion_prompts_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ An error occurred while generating fashion prompts."
        )
