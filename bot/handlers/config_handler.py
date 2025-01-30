from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import json
import logging
from ..utils.database import db
from ..services.prompt_styles.manager import style_manager

# Define the allowed parameters and their order
ALLOWED_PARAMS = {
    "gender": {
        "type": "str",
        "allowed_values": ["male", "female"],
        "description": "Género para la generación de imágenes",
    },
    "trigger_word": {
        "type": "str",
        "min_length": 1,
        "max_length": 50,
        "description": "Palabra clave para entrenamiento LoRA",
    },
    "model_endpoint": {
        "type": "str",
        "min_length": 1,
        "max_length": 200,
        "description": "Endpoint del modelo para generación de imágenes",
    },
    "style": {
        "type": "str",
        "description": "Estilo de los prompts generados",
        # allowed_values se validará en runtime
    },
    "num_outputs": {
        "type": "int",
        "min": 1,
        "max": 5,
        "description": "Número de imágenes a generar por prompt",
    },
    "num_inference_steps": {
        "type": "int",
        "min": 1,
        "max": 50,
        "description": "Calidad/velocidad trade-off",
    },
    "guidance_scale": {
        "type": "float",
        "min": 0,
        "max": 10,
        "description": "Controla qué tan cerca sigue el prompt",
    },
    "prompt_strength": {
        "type": "float",
        "min": 0,
        "max": 1,
        "description": "Balance entre prompt e imagen",
    },
}


async def config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /config command.
    If no arguments are provided, shows current configuration.
    If arguments are provided, updates the specified parameter.
    Format: /config [param] [value]
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logging.info(f"Config command received - User: {user_id} ({username})")

    # Get current config with defaults
    config = await db.get_user_config(user_id, ReplicateService.default_params.copy())

    # Add default gender if not present
    if "gender" not in config:
        config["gender"] = "male"

    # If no arguments provided, just show current config
    if len(context.args) == 0:
        # Format current configuration
        config_text = "⚙️ Configuración actual:\n\n"
        # Show all allowed parameters in a specific order
        param_order = [
            "gender",
            "trigger_word",
            "model_endpoint",
            "style",
            "num_outputs",
            "num_inference_steps",
            "guidance_scale",
            "prompt_strength",
        ]

        for param in param_order:
            if param in ALLOWED_PARAMS:
                value = config.get(param, "no configurado")
                config_text += f"`{param}`: `{value}`\n"

        await update.message.reply_text(config_text, parse_mode="Markdown")
        return

    # If arguments provided, try to update config
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Formato incorrecto. Usa `/config` para ver la configuración actual o `/help` para ver instrucciones.",
            parse_mode="Markdown",
        )
        return

    param, value = context.args[0].lower(), context.args[1]

    # Check if parameter exists
    if param not in ALLOWED_PARAMS:
        await update.message.reply_text(
            "❌ Parámetro no válido. Usa `/help` para ver los parámetros disponibles.",
            parse_mode="Markdown",
        )
        return

    # Convert and validate value
    try:
        if ALLOWED_PARAMS[param]["type"] == "float":
            value = float(value)
            if not (
                ALLOWED_PARAMS[param]["min"] <= value <= ALLOWED_PARAMS[param]["max"]
            ):
                raise ValueError(
                    f"El valor debe estar entre {ALLOWED_PARAMS[param]['min']} y {ALLOWED_PARAMS[param]['max']}"
                )
        elif ALLOWED_PARAMS[param]["type"] == "int":
            value = int(value)
            if not (
                ALLOWED_PARAMS[param]["min"] <= value <= ALLOWED_PARAMS[param]["max"]
            ):
                raise ValueError(
                    f"El valor debe estar entre {ALLOWED_PARAMS[param]['min']} y {ALLOWED_PARAMS[param]['max']}"
                )
        elif ALLOWED_PARAMS[param]["type"] == "str":
            if param == "style":
                # Validación especial para estilos en runtime
                available_styles = style_manager.get_available_styles()
                if value not in available_styles:
                    raise ValueError(
                        f"El estilo debe ser uno de: {', '.join(available_styles)}"
                    )
            elif "allowed_values" in ALLOWED_PARAMS[param]:
                if value not in ALLOWED_PARAMS[param]["allowed_values"]:
                    raise ValueError(
                        f"El valor debe ser uno de: {', '.join(ALLOWED_PARAMS[param]['allowed_values'])}"
                    )
            else:
                if not (
                    ALLOWED_PARAMS[param]["min_length"]
                    <= len(value)
                    <= ALLOWED_PARAMS[param]["max_length"]
                ):
                    raise ValueError(
                        f"La longitud debe estar entre {ALLOWED_PARAMS[param]['min_length']} y {ALLOWED_PARAMS[param]['max_length']} caracteres"
                    )

        # Get current config and update it
        config = await db.get_user_config(
            user_id, ReplicateService.default_params.copy()
        )
        config[param] = value
        await db.set_user_config(user_id, config)

        # Show success message with updated value
        await update.message.reply_text(
            f"✅ Configuración actualizada: `{param}` = `{value}`",
            parse_mode="Markdown",
        )

    except ValueError as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)}. Usa `/help` para más información.",
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(f"Error updating config: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Error inesperado al actualizar la configuración.",
            parse_mode="Markdown",
        )
