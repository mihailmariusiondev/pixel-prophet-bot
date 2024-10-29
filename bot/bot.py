import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from .handlers import (
    start_handler,
    help_handler,
    about_handler,
    error_handler,
    generate_handler,
    config_handler,
    variations_handler,
    last_generation_handler,
    analyze_image_handler,
    fashion_prompts_handler,
)
from .utils.logging_config import setup_logging


def run_bot():
    """
    Initialize and run the Telegram bot.
    """
    # Setup logging
    setup_logging()

    logging.info("Starting bot initialization...")
    # Create the Application and pass it your bot's token
    logging.info("Building application with token and timeouts...")
    application = (
        ApplicationBuilder()
        .token(
            os.getenv("BOT_TOKEN")
        )  # Retrieve the bot token from environment variables
        .read_timeout(30)  # Set read timeout for the bot
        .write_timeout(30)  # Set write timeout for the bot
        .connect_timeout(30)  # Set connection timeout for the bot
        .build()
    )
    logging.info("Application built successfully")

    # Register all handlers
    logging.info("Registering command handlers...")
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("about", about_handler))
    application.add_handler(CommandHandler("generate", generate_handler))
    application.add_handler(CommandHandler("config", config_handler))
    application.add_handler(CommandHandler("variations", variations_handler))
    application.add_handler(CommandHandler("last_generation", last_generation_handler))
    application.add_handler(CommandHandler("fashion", fashion_prompts_handler))

    application.add_handler(MessageHandler(filters.PHOTO, analyze_image_handler))
    logging.info("Command handlers registered")

    # Register error handler
    logging.info("Registering error handler...")
    application.add_error_handler(error_handler)  # Handle errors globally
    logging.info("Error handler registered")

    # Start the bot
    logging.info("All handlers registered. Starting bot polling...")
    application.run_polling()  # Start polling for updates
    logging.info("Bot polling started")
