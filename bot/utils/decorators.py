from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from ..services.replicate_service import ReplicateService
from ..utils.database import Database

db = Database()


def require_configured(func):
    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user_id = update.effective_user.id
        config = db.get_user_config(user_id, ReplicateService.default_params.copy())
        trigger_word = config.get("trigger_word")
        model_endpoint = config.get("model_endpoint")
        if not trigger_word or not model_endpoint:
            await update.message.reply_text(
                "❌ Configuración incompleta. Por favor, establece la palabra clave y el endpoint del modelo usando el comando `/config`."
            )
            return
        return await func(update, context, *args, **kwargs)

    return wrapper
