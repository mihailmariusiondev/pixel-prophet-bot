from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
from ..services.openai_service import generate_prompts
import logging
from ..utils.decorators import require_configured
from ..utils.database import db
import asyncio
import re
from ..services.prompt_styles.manager import style_manager


@require_configured
async def generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles concurrent image generation from text prompt.
    Supports two modes:
    1. Single prompt mode: /generate [prompt] - Generates num_outputs images of the same prompt
    2. Batch mode: /generate [number] - Generates exactly [number] different images from different prompts
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Generate command received - User: {user_id} ({username})")

    # Get the text after /generate
    text = (
        update.message.text.split(" ", 1)[1]
        if len(update.message.text.split(" ", 1)) > 1
        else ""
    )
    if not text:
        logging.warning(f"Empty input received - User: {user_id}")
        await update.message.reply_text(
            "Por favor, proporciona un prompt o un número para generar imágenes."
        )
        return

    try:
        # Get user config
        config = await db.get_user_config(
            user_id, ReplicateService.default_params.copy()
        )
        trigger_word = config.get("trigger_word")
        num_outputs = config.get("num_outputs", 1)  # Default to 1 if not set
        style = config.get("style", "professional")

        # If style is random, choose one for this batch and log it
        if style == "random":
            style = style_manager.get_random_style_name()
            logging.info(f"Random style selected for this batch: {style}")
            # Inform the user which style was selected
            await update.message.reply_text(
                f"🎲 Estilo aleatorio seleccionado: `{style}`", parse_mode="Markdown"
            )

        logging.info(
            f"User config loaded - Trigger Word: {trigger_word}, Num Outputs: {num_outputs}, Style: {style}"
        )

        # Check if input is a number (batch mode)
        if text.isdigit():
            num_prompts = min(int(text), 50)  # Limit to 50 prompts max
            logging.info(f"Batch mode detected - Requested prompts: {num_prompts}")
            status_message = await update.message.reply_text("⏳ Generando prompts...")

            # Generate prompts using OpenAI
            logging.info(
                f"Starting prompt generation for {num_prompts} prompts with style: {style}"
            )
            prompts = await generate_prompts(num_prompts, trigger_word, style)
            if not prompts:
                logging.error(f"Failed to generate prompts for user {user_id}")
                await status_message.edit_text("❌ Error al generar los prompts.")
                return

            logging.info(f"Successfully generated {len(prompts)} prompts")
            # Log each prompt's length for debugging
            for i, prompt in enumerate(prompts):
                logging.info(f"Prompt {i+1} length: {len(prompt)} characters")
                logging.info(f"Prompt {i+1} content: {prompt}")

            # Update status message
            await status_message.edit_text(f"⏳ Generando {len(prompts)} imágenes...")

            # Generate images concurrently for each prompt
            logging.info(
                f"Starting concurrent image generation for {len(prompts)} images"
            )
            try:
                async with asyncio.TaskGroup() as tg:
                    tasks = [
                        tg.create_task(
                            ReplicateService.generate_image(
                                prompt,
                                user_id=user_id,
                                message=update.message,
                                operation_type="batch",
                            )
                        )
                        for prompt in prompts
                    ]
                logging.info(
                    f"Successfully completed all {len(prompts)} image generations"
                )
            except ExceptionGroup as e:
                logging.error(f"Some tasks failed during batch generation: {str(e)}")
                # Continue to cleanup even if some tasks failed

            await status_message.delete()
            logging.info("Batch generation completed successfully")

        else:
            # Single prompt mode - here we DO use num_outputs
            prompt = text
            # Log the full prompt length and content
            logging.info(
                f"Single prompt mode - Full prompt length: {len(prompt)} characters"
            )
            logging.info(f"Single prompt mode - Full prompt content: {prompt}")

            status_text = (
                "⏳ Generando imagen..."
                if num_outputs == 1
                else f"⏳ Generando {num_outputs} imágenes..."
            )
            status_message = await update.message.reply_text(status_text)

            # Generate images concurrently
            logging.info(f"Starting concurrent generation of {num_outputs} images")
            try:
                async with asyncio.TaskGroup() as tg:
                    tasks = [
                        tg.create_task(
                            ReplicateService.generate_image(
                                prompt,
                                user_id=user_id,
                                message=update.message,
                                operation_type="single",
                            )
                        )
                        for _ in range(num_outputs)
                    ]
                logging.info(
                    f"Successfully completed all {num_outputs} image generations"
                )
            except ExceptionGroup as e:
                logging.error(
                    f"Some tasks failed during single prompt generation: {str(e)}"
                )
                # Continue to cleanup even if some tasks failed

            await status_message.delete()
            logging.info("Single prompt generation completed successfully")

    except Exception as e:
        logging.error(f"Error in generate handler: {str(e)}", exc_info=True)
        await update.message.reply_text("❌ Ha ocurrido un error inesperado.")
