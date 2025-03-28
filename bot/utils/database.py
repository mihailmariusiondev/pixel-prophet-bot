import aiosqlite
import json
from pathlib import Path
import logging
import sqlite3
import uuid


# Create a singleton instance
class Database:
    """
    Handles all database operations for the bot, including user configurations
    and generation history. Uses aiosqlite for asynchronous persistent storage
    with automatic timestamp tracking for updates.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.db_path = Path("bot_data.db")
            cls._instance.init_database()
        return cls._instance

    def init_database(self):
        """
        Initializes the database schema if it doesn't exist.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # User configurations table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_configs (
                        user_id INTEGER PRIMARY KEY,
                        config TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    async def get_user_config(self, user_id, default_config):
        """
        Retrieves user-specific configuration or falls back to defaults.
        Uses asynchronous context manager for automatic connection handling.

        Args:
            user_id: Telegram user ID
            default_config: Configuration to use if user has no saved config

        Returns:
            dict: User's configuration or default if none exists
        """
        try:
            logging.info(f"Retrieving config for user {user_id}")
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    "SELECT config FROM user_configs WHERE user_id = ?", (user_id,)
                )
                result = await cursor.fetchone()

                if result:
                    logging.info(f"Found existing config for user {user_id}")
                    return json.loads(result[0])
                else:
                    logging.info(f"No config found for user {user_id}, using default")
                    return default_config

        except Exception as e:
            logging.error(f"Error retrieving user config: {e}", exc_info=True)
            return default_config

    async def set_user_config(self, user_id, config):
        """
        Updates or creates user configuration using UPSERT pattern.
        Automatically handles JSON serialization of config data.

        Args:
            user_id: Telegram user ID
            config: Dictionary containing user's configuration
        """
        try:
            logging.info(f"Updating config for user {user_id}")
            logging.info(f"New config: {config}")
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    """
                    INSERT INTO user_configs (user_id, config)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        config=excluded.config,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (user_id, json.dumps(config)),
                )
                await conn.commit()
                logging.info(f"Successfully updated config for user {user_id}")

        except Exception as e:
            logging.error(f"Error setting user config: {e}", exc_info=True)
            raise

    async def save_prediction(self, user_id, prompt, output_url):
        """
        Save prediction data with unique prediction_id using full UUID
        """
        try:
            prediction_id = str(
                uuid.uuid4()
            )  # UUID completo, ej: 550e8400-e29b-41d4-a716-446655440000
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    """
                    INSERT INTO predictions
                    (prediction_id, user_id, prompt, output_url)
                    VALUES (?, ?, ?, ?)
                    """,
                    (prediction_id, user_id, prompt, output_url),
                )
                await conn.commit()
                return prediction_id
        except Exception as e:
            logging.error(f"Error saving prediction: {e}", exc_info=True)
            raise

    async def get_prediction(self, prediction_id):
        """
        Retrieve prediction data by prediction_id
        """
        try:
            logging.info(f"Retrieving prediction data for ID: {prediction_id}")
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    """
                    SELECT prompt, output_url
                    FROM predictions
                    WHERE prediction_id = ?
                    """,
                    (prediction_id,),
                )
                result = await cursor.fetchone()
                if result:
                    logging.info(f"Found prediction data for ID: {prediction_id}")
                else:
                    logging.info(f"No prediction data found for ID: {prediction_id}")
                return result
        except Exception as e:
            logging.error(f"Error retrieving prediction: {e}", exc_info=True)
            return None


# Create the singleton instance
db = Database()

# Export the singleton instance
__all__ = ["db"]
