from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
import json
import logging
from ..utils import Database

db = Database()


async def config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /config command to view or modify generation parameters.
    Allows users to customize their image generation settings.

    Args:
        update: Telegram update containing command and parameters
        context: Bot context containing command arguments
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    args = context.args
    logging.info(f"Config command received from user {user_id} ({username}) with args: {args}")

    try:
        # Show current config if no arguments
        if not args:
            logging.debug(f"Showing current config for user {user_id}")
            config = db.get_user_config(user_id, ReplicateService.default_params)
            logging.info(f"Current config for user {user_id}: {json.dumps(config)}")

            message = (
                "🛠️ *Configuración actual:*\n\n"
                f"`{json.dumps(config, indent=2)}`\n\n"
                "Para modificar un parámetro usa:\n"
                "`/config <parámetro> <valor>`\n\n"
                "Ejemplo:\n"
                "`/config seed 42`\n"
                "`/config guidance_scale 7.5`"
            )
            await update.message.reply_text(message, parse_mode="MarkdownV2")
            return

        # Validate argument format
        if len(args) != 2:
            logging.warning(f"Invalid config format from user {user_id}: {args}")
            await update.message.reply_text(
                "❌ Formato incorrecto. Usa:\n"
                "/config <parámetro> <valor>"
            )
            return

        param, value = args[0], args[1]
        logging.info(f"Config update request - User: {user_id}, Param: {param}, Value: {value}")

        # Get current config
        config = db.get_user_config(user_id, ReplicateService.default_params.copy())
        old_value = config.get(param)
        logging.debug(f"Current value for {param}: {old_value}")

        # Validate parameter exists
        if param not in ReplicateService.default_params:
            logging.warning(f"Invalid parameter '{param}' requested by user {user_id}")
            await update.message.reply_text(
                f"❌ Parámetro '{param}' no válido.\n"
                f"Parámetros disponibles:\n"
                f"{', '.join(ReplicateService.default_params.keys())}"
            )
            return

        # Convert value to correct type
        try:
            original_value = ReplicateService.default_params[param]
            logging.debug(f"Converting value from {type(value).__name__} to {type(original_value).__name__}")

            if isinstance(original_value, bool):
                value = value.lower() in ("true", "1", "yes")
            elif isinstance(original_value, int):
                value = int(value)
            elif isinstance(original_value, float):
                value = float(value)

            logging.debug(f"Value converted successfully: {value}")

        except ValueError:
            logging.warning(f"Invalid value type for parameter {param} from user {user_id}: {value}")
            await update.message.reply_text(
                f"❌ Valor no válido para {param}. "
                f"Debe ser del tipo: {type(original_value).__name__}"
            )
            return

        # Update the config
        config[param] = value
        db.set_user_config(user_id, config)
        logging.info(
            f"Config updated - User: {user_id}, Param: {param}, Old: {old_value}, New: {value}"
        )

        # Escape special characters for MarkdownV2
        old_value_str = str(old_value).replace(".", "\\.").replace("-", "\\-")
        new_value_str = str(value).replace(".", "\\.").replace("-", "\\-")
        param_str = param.replace(".", "\\.").replace("-", "\\-")

        # Create message with updated config
        message = (
            "✅ *Parámetro actualizado:*\n"
            f"`{param_str}`: ~`{old_value_str}`~ → `{new_value_str}`\n\n"
            "🛠️ *Configuración actual:*\n\n"
            f"`{json.dumps(config, indent=2)}`"
        )

        await update.message.reply_text(message, parse_mode="MarkdownV2")

    except Exception as e:
        logging.error(f"Error in config_handler for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error al procesar la configuración."
        )
