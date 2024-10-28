import sqlite3
import json
from pathlib import Path
import logging


class Database:
    """
    Handles all database operations for the bot, including user configurations
    and generation history. Uses SQLite for persistent storage with automatic
    timestamp tracking for updates.
    """

    def __init__(self):
        # Store database path as a Path object for cross-platform compatibility
        self.db_path = Path("bot_data.db")
        self.init_database()

    def init_database(self):
        """
        Initializes the database schema if it doesn't exist.
        Creates tables with appropriate constraints and defaults.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # User configurations table with automatic timestamp updates
                # Stores JSON-serialized config data for flexibility
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_configs (
                        user_id INTEGER PRIMARY KEY,
                        config TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    def get_user_config(self, user_id, default_config):
        """
        Retrieves user-specific configuration or falls back to defaults.
        Uses context manager for automatic connection handling.

        Args:
            user_id: Telegram user ID
            default_config: Configuration to use if user has no saved config

        Returns:
            dict: User's configuration or default if none exists
        """
        try:
            logging.debug(f"Retrieving config for user {user_id}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT config FROM user_configs WHERE user_id = ?", (user_id,)
                )
                result = cursor.fetchone()

                if result:
                    logging.debug(f"Found existing config for user {user_id}")
                    return json.loads(result[0])
                else:
                    logging.debug(f"No config found for user {user_id}, using default")
                    return default_config

        except Exception as e:
            logging.error(f"Error retrieving user config: {e}", exc_info=True)
            return default_config

    def set_user_config(self, user_id, config):
        """
        Updates or creates user configuration using UPSERT pattern.
        Automatically handles JSON serialization of config data.

        Args:
            user_id: Telegram user ID
            config: Dictionary containing user's configuration
        """
        try:
            logging.info(f"Updating config for user {user_id}")
            logging.debug(f"New config: {config}")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO user_configs (user_id, config)
                    VALUES (?, ?)
                """,
                    (user_id, json.dumps(config)),
                )
                conn.commit()
                logging.debug(f"Successfully updated config for user {user_id}")

        except Exception as e:
            logging.error(f"Error setting user config: {e}", exc_info=True)
            raise

    def get_last_generation(self, user_id):
        """Get user's last generation parameters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT params FROM last_generations WHERE user_id = ?", (user_id,)
                )
                result = cursor.fetchone()
                return json.loads(result[0]) if result else None
        except Exception as e:
            logging.error(f"Error getting last generation: {e}")
            return None

    def set_last_generation(self, user_id, params):
        """Save or update user's last generation parameters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO last_generations (user_id, params)
                    VALUES (?, ?)
                """,
                    (user_id, json.dumps(params)),
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Error setting last generation: {e}")
            raise
