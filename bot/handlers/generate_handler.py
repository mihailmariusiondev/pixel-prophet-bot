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
    Supports multiple modes:
    1. Single prompt mode: /generate [prompt] - Generates num_outputs images of the same prompt
    2. Batch mode with styles: /generate [number] styles=style1,style2 - Generates images with specified styles
    3. Batch mode default: /generate [number] - Generates images with user's default style
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
        num_outputs = config.get("num_outputs", 1)

        # Check if input starts with a number (batch mode)
        first_word = text.split()[0]
        if first_word.isdigit():
            num_prompts = min(int(first_word), 50)  # Limit to 50 prompts max
            remaining_text = text[len(first_word) :].strip()

            # Check for styles parameter
            styles = []
            if remaining_text.startswith("styles="):
                styles_part = remaining_text.split()[0]
                styles = styles_part.replace("styles=", "").split(",")
                # Validate styles
                available_styles = style_manager.get_available_styles()
                invalid_styles = [s for s in styles if s not in available_styles]
                if invalid_styles:
                    await update.message.reply_text(
                        f"❌ Estilos inválidos: {', '.join(invalid_styles)}\n"
                        f"Estilos disponibles: {', '.join(available_styles)}"
                    )
                    return
            else:
                # Use default style from config
                styles = [config.get("style", "professional")]

            logging.info(
                f"Batch mode detected - Requested prompts: {num_prompts}, Styles: {styles}"
            )
            status_message = await update.message.reply_text("⏳ Generando prompts...")

            # Generate prompts for each style
            all_prompts = []
            prompts_per_style = num_prompts // len(styles)
            remainder = num_prompts % len(styles)

            for style in styles:
                style_prompts = await generate_prompts(
                    prompts_per_style + (1 if remainder > 0 else 0), trigger_word, style
                )
                if not style_prompts:
                    logging.error(f"Failed to generate prompts for style {style}")
                    continue
                all_prompts.extend(style_prompts)
                if remainder > 0:
                    remainder -= 1

            if not all_prompts:
                logging.error(f"Failed to generate any prompts for user {user_id}")
                await status_message.edit_text("❌ Error al generar los prompts.")
                return

            # Update status message
            await status_message.edit_text(
                f"⏳ Generando {len(all_prompts)} imágenes..."
            )

            # Generate images concurrently
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
                        for prompt in all_prompts
                    ]
            except ExceptionGroup as e:
                logging.error(f"Some tasks failed during batch generation: {str(e)}")

            await status_message.delete()
            logging.info("Batch generation completed successfully")

        else:
            # Single prompt mode - use num_outputs from config
            prompt = text
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
            except ExceptionGroup as e:
                logging.error(
                    f"Some tasks failed during single prompt generation: {str(e)}"
                )

            await status_message.delete()
            logging.info("Single prompt generation completed successfully")

    except Exception as e:
        logging.error(f"Error in generate handler: {str(e)}", exc_info=True)
        await update.message.reply_text("❌ Ha ocurrido un error inesperado.")
