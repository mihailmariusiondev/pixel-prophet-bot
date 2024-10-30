# bot/handlers/fashion_prompts_handler.py

from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.database import Database
from ..utils.decorators import require_configured

db = Database()


@require_configured
async def fashion_prompts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generate multiple fashion prompts and create corresponding images.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Fashion prompts generation requested by user {user_id} ({username})")

    try:
        config = db.get_user_config(user_id, ReplicateService.default_params.copy())
        trigger_word = config.get("trigger_word")
        model_endpoint = config.get("model_endpoint")

        prompts = []
        system_prompt = f"""You are a world-class prompt engineer specializing in creating exceptional, highly detailed prompts for AI text-to-image tools. Your expertise lies in crafting prompts that result in photorealistic, hyper-realistic images.
        Create a single prompt with these key elements:
        - MUST start with '{trigger_word}'
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
                clean_prompt = " ".join(prompt.strip().split())
                if clean_prompt.startswith(trigger_word):
                    prompts.append(clean_prompt)

        if not prompts:
            await update.message.reply_text("❌ Error generating prompts.")
            return

        for prompt in prompts:
            await ReplicateService.generate_image(
                prompt, user_id=user_id, message=update.message
            )

    except Exception as e:
        logging.error(
            f"Error in fashion_prompts_handler for user {user_id}: {str(e)}",
            exc_info=True,
        )
        await update.message.reply_text(
            "❌ Ocurrió un error mientras se generaban los fashion prompts."
        )
