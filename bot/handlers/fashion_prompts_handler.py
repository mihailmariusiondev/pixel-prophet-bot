from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService


async def fashion_prompts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generate multiple fashion prompts and create corresponding images.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Fashion prompts generation requested by user {user_id} ({username})")

    try:
        # Send initial status message
        status_message = await update.message.reply_text(
            "🎭 Generating fashion prompts..."
        )

        prompts = []
        # Define system prompt for consistent fashion-focused results
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

        # Generate three unique prompts
        for i in range(3):
            logging.debug(f"Generating prompt {i+1}/3 for user {user_id}")
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
                # Clean and validate prompt
                clean_prompt = " ".join(prompt.strip().split())
                if clean_prompt.startswith("MARIUS"):
                    prompts.append(clean_prompt)
                    logging.debug(
                        f"Generated valid prompt {i+1}: {clean_prompt[:100]}..."
                    )
                else:
                    logging.warning(
                        f"Generated prompt {i+1} invalid - doesn't start with MARIUS"
                    )
            else:
                logging.error(f"Failed to generate prompt {i+1} for user {user_id}")

        if not prompts:
            logging.error(f"Failed to generate any valid prompts for user {user_id}")
            await status_message.edit_text("❌ Error generating prompts.")
            return

        # Generate images for each prompt
        logging.info(
            f"Starting image generation for {len(prompts)} prompts - User: {user_id}"
        )
        await status_message.edit_text("🎨 Generating images from prompts...")

        for i, prompt in enumerate(prompts, 1):
            logging.debug(f"Generating image {i}/{len(prompts)} for user {user_id}")
            await ReplicateService.generate_image(
                prompt, user_id=user_id, message=update.message
            )

        await status_message.edit_text("✅ Fashion prompt generation completed!")
        logging.info(f"Completed fashion prompt generation for user {user_id}")

    except Exception as e:
        logging.error(
            f"Error in fashion_prompts_handler for user {user_id}: {str(e)}",
            exc_info=True,
        )
        await update.message.reply_text(
            "❌ An error occurred while generating fashion prompts."
        )
