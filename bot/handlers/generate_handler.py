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
        default_style = config.get("style", "professional")

        # Parse command
        mode, params = parse_generate_command(text, trigger_word, default_style)

        # Handle based on mode
        if mode == "single_prompt":
            await handle_single_prompt(
                update, params["prompt"], config.get("num_outputs", 1)
            )

        elif mode == "batch_direct_prompt":
            await handle_batch_direct_prompt(
                update, params["prompt"], params["num_outputs"]
            )

        elif mode == "batch_styles":
            await handle_batch_styles(
                update,
                params["num_outputs"],
                params["styles"],
                trigger_word,
                config.get("gender", "male"),
            )

        elif mode == "batch_default_style":
            gender = config.get("gender", "male")
            await handle_batch_default_style(
                update, params["num_outputs"], trigger_word, default_style, gender
            )

        elif mode == "invalid":
            await update.message.reply_text(f"❌ {params['reason']}")
            return

        else:
            await update.message.reply_text("Formato de comando no válido")

    except Exception as e:
        logging.error(f"Error in generate handler: {str(e)}", exc_info=True)
        await update.message.reply_text("❌ Ha ocurrido un error inesperado.")


# Helper functions
def parse_generate_command(
    text: str, trigger_word: str, default_style: str
) -> tuple[str, dict]:
    text = text.strip()

    # Nuevo caso: styles= sin número primero
    if text.startswith("styles="):
        styles_part = text.split("styles=")[1].split()[0]
        styles = [s.strip() for s in styles_part.split(",")]
        return "batch_styles", {"num_outputs": 1, "styles": styles}

    # Modificar detección de números para evitar falsos positivos
    if text and text[0].isdigit():
        parts = text.split()
        try:
            num_outputs = min(int(parts[0]), 50)
            remaining = " ".join(parts[1:])
        except ValueError:
            num_outputs = 1
            remaining = text
    else:
        num_outputs = 1
        remaining = text

    # Validar styles= en cualquier posición después del número
    if "styles=" in remaining:
        styles_part = remaining.split("styles=")[1].split()[0]
        styles = [s.strip() for s in styles_part.split(",")]
        remaining = remaining.replace(f"styles={styles_part}", "").strip()

        # Si queda texto después de styles=, es parte del prompt
        if remaining:
            return "invalid", {
                "reason": "No se puede mezclar styles= con prompt directo"
            }

        return "batch_styles", {"num_outputs": num_outputs, "styles": styles}

    # Mode 1: Direct prompt (/generate prompt)
    if not text[0].isdigit():
        return "single_prompt", {"prompt": f"{trigger_word} {text}"}

    # Mode 4: Just number (/generate 3)
    return "batch_default_style", {"num_outputs": num_outputs, "styles": ["random"]}


async def handle_single_prompt(update: Update, prompt: str, num_outputs: int):
    status = await update.message.reply_text(f"⏳ Generando {num_outputs} imágenes...")

    try:
        async with asyncio.TaskGroup() as tg:
            [
                tg.create_task(
                    ReplicateService.generate_image(
                        prompt,
                        user_id=update.effective_user.id,
                        message=update.message,
                        operation_type="single",
                    )
                )
                for _ in range(num_outputs)
            ]
    except ExceptionGroup as e:
        logging.error(f"Error en generación simple: {str(e)}")

    await status.delete()


async def handle_batch_direct_prompt(update: Update, prompt: str, num_outputs: int):
    status = await update.message.reply_text(f"⏳ Generando {num_outputs} imágenes...")

    try:
        async with asyncio.TaskGroup() as tg:
            [
                tg.create_task(
                    ReplicateService.generate_image(
                        prompt,
                        user_id=update.effective_user.id,
                        message=update.message,
                        operation_type="batch",
                    )
                )
                for _ in range(num_outputs)
            ]
    except ExceptionGroup as e:
        logging.error(f"Error en batch directo: {str(e)}")

    await status.delete()


async def handle_batch_styles(
    update: Update, num_outputs: int, styles: list, trigger_word: str, gender: str
):
    # Validate styles
    available_styles = style_manager.get_available_styles()
    if invalid := [s for s in styles if s not in available_styles]:
        await update.message.reply_text(f"❌ Estilos inválidos: {', '.join(invalid)}")
        return

    # Generate prompts
    status = await update.message.reply_text("⏳ Generando prompts...")
    prompts = await generate_prompts(
        num_outputs, trigger_word, style=styles[0], gender=gender
    )

    # Generate images
    await status.edit_text(f"⏳ Generando {len(prompts)} imágenes...")

    try:
        async with asyncio.TaskGroup() as tg:
            [
                tg.create_task(
                    ReplicateService.generate_image(
                        p,
                        user_id=update.effective_user.id,
                        message=update.message,
                        operation_type="batch",
                    )
                )
                for p in prompts
            ]
    except ExceptionGroup as e:
        logging.error(f"Error en batch con estilos: {str(e)}")

    await status.delete()


async def handle_batch_default_style(
    update: Update, num_outputs: int, trigger_word: str, default_style: str, gender: str
):
    await handle_batch_styles(update, num_outputs, ["random"], trigger_word, gender)
