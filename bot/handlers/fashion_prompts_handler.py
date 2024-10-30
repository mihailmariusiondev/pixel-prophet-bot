from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..services.openai_service import chat_completion
from ..services.replicate_service import ReplicateService
from ..utils.database import Database
from ..utils.decorators import require_configured
from ..utils.prompt_templates import get_fashion_messages

db = Database()


@require_configured
async def fashion_prompts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generate multiple fashion prompts and create corresponding images.
    Uses OpenAI to generate fashion-specific prompts and creates images for each.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Fashion prompts generation requested - User: {user_id} ({username})")

    try:
        # Get user configuration
        config = db.get_user_config(user_id, ReplicateService.default_params.copy())
        trigger_word = config.get("trigger_word")
        model_endpoint = config.get("model_endpoint")
        logging.info(
            f"Configuration retrieved - User: {user_id}, Trigger Word: {trigger_word}"
        )

        # Initialize prompts collection
        prompts = []

        # Define system prompt for fashion generation
        system_prompt = f"""You are a world-class prompt engineer..."""
        logging.debug(f"System prompt prepared - User: {user_id}")

        # Generate three unique prompts
        for i in range(3):
            logging.info(f"Generating prompt {i+1}/3 - User: {user_id}")

            # Request prompt from OpenAI
            prompt = await chat_completion(
                messages=get_fashion_messages(trigger_word),
                temperature=0.7,
            )

            # Validate and clean prompt
            if prompt:
                clean_prompt = " ".join(prompt.strip().split())
                if clean_prompt.startswith(trigger_word):
                    prompts.append(clean_prompt)
                    logging.info(f"Valid prompt {i+1} generated - User: {user_id}")
                else:
                    logging.warning(
                        f"Invalid prompt format {i+1} (missing trigger word) - User: {user_id}"
                    )

        # Handle case where no valid prompts were generated
        if not prompts:
            logging.error(f"No valid prompts generated - User: {user_id}")
            await update.message.reply_text("❌ Error generating prompts.")
            return

        # Generate images for each valid prompt
        for i, prompt in enumerate(prompts, 1):
            logging.info(
                f"Starting image generation {i}/{len(prompts)} - User: {user_id}"
            )
            await ReplicateService.generate_image(
                prompt,
                user_id=user_id,
                message=update.message,
                operation_type="fashion",
            )

    except Exception as e:
        logging.error(
            f"Error in fashion_prompts_handler - User: {user_id}", exc_info=True
        )
        await update.message.reply_text(
            "❌ Ocurrió un error mientras se generaban los fashion prompts."
        )
