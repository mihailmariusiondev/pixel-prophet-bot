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
        if mode == "batch_direct_prompt":
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
            await update.message.reply_text(f"{params['reason']}")
            return

    except Exception as e:
        logging.error(f"Error in generate handler: {str(e)}", exc_info=True)
        error_messages = {
            "invalid_style": "❌ Estilo no válido. Usa /help para ver la lista",
            "mixed_formats": "❌ No mezcles prompt directo con styles=",
            "max_limit": "❌ Máximo 50 imágenes por comando",
            "style_syntax": "❌ Formato incorrecto para styles. Usa styles=estilo1,estilo2",
        }
        await update.message.reply_text(
            error_messages.get(str(e), "❌ Error desconocido")
        )


# Helper functions
def parse_generate_command(
    text: str, trigger_word: str, default_style: str
) -> tuple[str, dict]:
    text = text.strip().lower()

    if not text:
        return "invalid", {
            "reason": "❌ Formato inválido. Debes especificar un número al inicio"
        }

    # Extraer número obligatorio
    parts = text.split(maxsplit=1)
    if not parts[0].isdigit():
        return "invalid", {"reason": "❌ Debes especificar un número al inicio"}

    try:
        num_outputs = min(int(parts[0]), 50)
        remaining = parts[1] if len(parts) > 1 else ""
    except ValueError:
        return "invalid", {"reason": "❌ Número inválido"}

    # Manejar styles=
    if "styles=" in remaining:
        styles_part = remaining.split("styles=")[-1].split()[0]
        styles = [s.strip().lower() for s in styles_part.split(",") if s.strip()]
        remaining = remaining.replace(f"styles={styles_part}", "").strip()

        if remaining:
            return "invalid", {
                "reason": "❌ No puedes mezclar estilos con un prompt directo"
            }

        return "batch_styles", {"num_outputs": num_outputs, "styles": styles}

    # Modo batch con prompt directo
    if remaining:
        return "batch_direct_prompt", {
            "num_outputs": num_outputs,
            "prompt": f"{trigger_word} {remaining}",
        }

    # Modo estilo por defecto
    return "batch_default_style", {"num_outputs": num_outputs, "styles": ["random"]}


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
    user_id = update.effective_user.id
    logging.info(f"[User {user_id}] Iniciando generación con estilos: {styles}")

    # Validar estilos y eliminar duplicados
    available_styles = style_manager.get_available_styles()
    valid_styles = list({s for s in styles if s in available_styles})

    logging.debug(
        f"[User {user_id}] Estilos recibidos: {styles} | Válidos: {valid_styles}"
    )

    if not valid_styles:
        logging.warning(
            f"[User {user_id}] No se encontraron estilos válidos en: {styles}"
        )
        await update.message.reply_text("❌ Ningún estilo válido encontrado")
        return

    # Calcular imágenes por estilo
    images_per_style = num_outputs
    total_images = images_per_style * len(valid_styles)

    logging.info(
        f"[User {user_id}] Configuración final: "
        f"{len(valid_styles)} estilos x {images_per_style} imágenes = {total_images} total"
    )

    status = await update.message.reply_text(
        f"⏳ Generando {total_images} imágenes ({len(valid_styles)} estilos)..."
    )

    try:
        async with asyncio.TaskGroup() as tg:
            for style in valid_styles:
                logging.debug(f"[User {user_id}] Procesando estilo: {style}")

                # Generar prompts para cada estilo
                logging.info(
                    f"[User {user_id}] Generando {images_per_style} prompts para estilo: {style}"
                )
                prompts = await generate_prompts(
                    images_per_style, trigger_word, style=style, gender=gender
                )

                logging.debug(
                    f"[User {user_id}] Prompts generados para {style}: {len(prompts)}"
                )
                if prompts:
                    logging.debug(
                        f"[User {user_id}] Ejemplo de prompt ({style}): {prompts[0][:100]}..."
                    )

                # Crear tareas para cada prompt
                logging.info(
                    f"[User {user_id}] Creando {len(prompts)} tareas de generación para {style}"
                )
                [
                    tg.create_task(
                        ReplicateService.generate_image(
                            p,
                            user_id=user_id,
                            message=update.message,
                            operation_type="batch",
                        )
                    )
                    for p in prompts
                ]

            logging.info(
                f"[User {user_id}] Total de tareas creadas: {len(valid_styles) * images_per_style}"
            )

    except ExceptionGroup as e:
        logging.error(
            f"[User {user_id}] Error en generación por estilos: {str(e)}", exc_info=True
        )
        await update.message.reply_text("⚠️ Algunas imágenes fallaron en la generación")

    await status.delete()
    logging.info(
        f"[User {user_id}] Generación completada - {total_images} imágenes procesadas"
    )


async def handle_batch_default_style(
    update: Update, num_outputs: int, trigger_word: str, default_style: str, gender: str
):
    await handle_batch_styles(update, num_outputs, ["random"], trigger_word, gender)
