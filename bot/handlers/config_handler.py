from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import json
import logging
from ..utils import Database

db = Database()

# Define the allowed parameters and their order
ALLOWED_PARAMS = {
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
}

async def config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /config command to view or modify generation parameters.
    Only allows modification of specific approved parameters within defined limits.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    args = context.args
    logging.info(
        f"Config command received from user {user_id} ({username}) with args: {args}"
    )
    try:
        # Show current config if no arguments
        if not args:
            logging.debug(f"Showing current config for user {user_id}")
            config = db.get_user_config(user_id, ReplicateService.default_params)
            # Create ordered filtered config using ALLOWED_PARAMS order
            filtered_config = {
                param: config.get(param) for param in ALLOWED_PARAMS if param in config
            }
            # Create help message with parameter limits, properly escaped
            help_text = (
                "• `num_inference_steps`: Calidad/velocidad trade-off (1-50)\n"
                "• `guidance_scale`: Controla qué tan cerca sigue el prompt (0-10)\n"
                "• `prompt_strength`: Balance entre prompt e imagen (0-1)\n"
                "• `trigger_word`: Palabra clave para entrenamiento LoRA (1-50 caracteres)\n"
                "• `model_endpoint`: Endpoint del modelo para generación de imágenes (1-200 caracteres)"
            )
            message = (
                "🛠️ *Configuración actual:*\n\n"
                f"`{json.dumps(filtered_config, indent=2)}`\n\n"
                "📝 *Parámetros disponibles:*\n"
                f"{help_text}\n\n"
                "Para modificar usa:\n"
                "`/config <parámetro> <valor>`\n\n"
                "Ejemplo:\n"
                "`/config guidance_scale 7.5`"
            )
            logging.debug(f"Sending current configuration to user {user_id}")
            await update.message.reply_text(message, parse_mode="Markdown")
            logging.info(f"Current configuration sent to user {user_id}")
            return

        # Validate argument format
        if len(args) != 2:
            logging.warning(f"Invalid config format from user {user_id}: {args}")
            await update.message.reply_text(
                "❌ Formato incorrecto. Usa:\n" "/config <parámetro> <valor>"
            )
            return

        param, value = args[0], args[1]
        logging.debug(f"User {user_id} attempting to update parameter '{param}' with value '{value}'")

        # Validate parameter is allowed
        if param not in ALLOWED_PARAMS:
            logging.warning(f"Invalid parameter '{param}' requested by user {user_id}")
            await update.message.reply_text(
                f"❌ Parámetro '{param}' no válido.\n"
                f"Parámetros disponibles:\n"
                f"{', '.join(ALLOWED_PARAMS.keys())}"
            )
            return

        # Convert and validate value
        try:
            if ALLOWED_PARAMS[param]["type"] == "float":
                value = float(value)
                if not (
                    ALLOWED_PARAMS[param]["min"]
                    <= value
                    <= ALLOWED_PARAMS[param]["max"]
                ):
                    raise ValueError(
                        f"Value must be between {ALLOWED_PARAMS[param]['min']} and {ALLOWED_PARAMS[param]['max']}"
                    )
            elif ALLOWED_PARAMS[param]["type"] == "int":
                value = int(value)
                if not (
                    ALLOWED_PARAMS[param]["min"]
                    <= value
                    <= ALLOWED_PARAMS[param]["max"]
                ):
                    raise ValueError(
                        f"Value must be between {ALLOWED_PARAMS[param]['min']} and {ALLOWED_PARAMS[param]['max']}"
                    )
            elif ALLOWED_PARAMS[param]["type"] == "str":
                if not (
                    ALLOWED_PARAMS[param]["min_length"]
                    <= len(value)
                    <= ALLOWED_PARAMS[param]["max_length"]
                ):
                    raise ValueError(
                        f"Length must be entre {ALLOWED_PARAMS[param]['min_length']} y {ALLOWED_PARAMS[param]['max_length']} caracteres"
                    )
            else:
                raise ValueError("Unsupported parameter type")
            logging.debug(f"Parameter '{param}' validated successfully with value '{value}'")
        except ValueError as e:
            logging.warning(
                f"Invalid value for parameter {param} from user {user_id}: {value}. Error: {str(e)}"
            )
            await update.message.reply_text(
                f"❌ Valor no válido para `{param}`.\n{str(e)}"
            )
            return

        # Update the config
        config = db.get_user_config(user_id, ReplicateService.default_params.copy())
        old_value = config.get(param)
        config[param] = value
        db.set_user_config(user_id, config)
        logging.info(
            f"Config updated - User: {user_id}, Param: {param}, Old: {old_value}, New: {value}"
        )

        # Show updated config (filtered to allowed params only)
        filtered_config = {k: v for k, v in config.items() if k in ALLOWED_PARAMS}
        message = (
            "✅ *Parámetro actualizado:*\n"
            f"`{param}`: `{old_value}` → `{value}`\n\n"
            "🛠️ *Configuración actual:*\n\n"
            f"`{json.dumps(filtered_config, indent=2)}`"
        )
        logging.debug(f"Sending updated configuration to user {user_id}")
        await update.message.reply_text(message, parse_mode="Markdown")
        logging.info(f"Updated configuration sent to user {user_id}")
    except Exception as e:
        logging.error(f"Error in config_handler for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error al procesar la configuración."
        )
