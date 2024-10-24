import logging
from logging.handlers import RotatingFileHandler
import os

# Get the root logger
logger = logging.getLogger()
# Set the logging level to INFO
logger.setLevel(logging.INFO)

# Define the directory for log files
log_dir = "logs"
# Create the log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a rotating file handler
file_handler = RotatingFileHandler(
    os.path.join(log_dir, "bot.log"), maxBytes=10 * 1024 * 1024, backupCount=5
)
file_handler.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Define the log message format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Set the formatter for both handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
