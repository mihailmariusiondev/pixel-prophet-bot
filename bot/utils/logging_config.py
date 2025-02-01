import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging():
    # Eliminar handlers existentes
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Configuración básica
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Niveles disponibles
    valid_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # Verificar y establecer nivel
    level = valid_levels.get(log_level, logging.INFO)
    root.setLevel(level)

    # Configurar directorio de logs
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configurar handler de archivo rotativo
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "bot.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    # Configurar handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    # Añadir handlers
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    # Log de prueba
    logging.info("Configuración de logging completada")
    logging.debug(f"Nivel de log configurado: {log_level}")
