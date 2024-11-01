import aiosqlite
import json
from pathlib import Path
import logging

# Create a singleton instance
class Database:
    """
    Handles all database operations for the bot using aiosqlite for async support.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.db_path = Path("bot_data.db")
        return cls._instance

    async def init_database(self):
        """
        Initializes the database schema if it doesn't exist.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_configs (
                        user_id INTEGER PRIMARY KEY,
                        config TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        prediction_id TEXT PRIMARY KEY,
                        user_id INTEGER,
                        prompt TEXT,
                        input_params TEXT,
                        output_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user_configs(user_id)
                    )
                """)
                await conn.commit()
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    async def get_user_config(self, user_id, default_config):
        """
        Retrieves user-specific configuration asynchronously.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute(
                    "SELECT config FROM user_configs WHERE user_id = ?",
                    (user_id,)
                ) as cursor:
                    result = await cursor.fetchone()
                    if result:
                        return json.loads(result[0])
                    return default_config
        except Exception as e:
            logging.error(f"Error retrieving user config: {e}", exc_info=True)
            return default_config

    async def set_user_config(self, user_id, config):
        """
        Updates or creates user configuration asynchronously.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    """
                    INSERT OR REPLACE INTO user_configs (user_id, config)
                    VALUES (?, ?)
                    """,
                    (user_id, json.dumps(config))
                )
                await conn.commit()
        except Exception as e:
            logging.error(f"Error setting user config: {e}", exc_info=True)
            raise

    async def save_prediction(self, prediction_id, user_id, prompt, input_params, output_url):
        """
        Save prediction data asynchronously.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    """
                    INSERT INTO predictions
                    (prediction_id, user_id, prompt, input_params, output_url)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (prediction_id, user_id, prompt, input_params, output_url)
                )
                await conn.commit()
        except Exception as e:
            logging.error(f"Error saving prediction: {e}", exc_info=True)
            # Don't raise the error, just log it
            pass

    async def get_prediction(self, prediction_id):
        """
        Retrieve prediction data asynchronously.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute(
                    """
                    SELECT prompt, input_params, output_url
                    FROM predictions
                    WHERE prediction_id = ?
                    """,
                    (prediction_id,)
                ) as cursor:
                    return await cursor.fetchone()
        except Exception as e:
            logging.error(f"Error retrieving prediction: {e}", exc_info=True)
            return None

    async def get_last_prediction(self, user_id):
        """
        Get the most recent prediction asynchronously.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute(
                    """
                    SELECT prompt, input_params, output_url, prediction_id
                    FROM predictions
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (user_id,)
                ) as cursor:
                    return await cursor.fetchone()
        except Exception as e:
            logging.error(f"Error retrieving last prediction: {e}", exc_info=True)
            return None

# Create the singleton instance
db = Database()

# Export the singleton instance
__all__ = ['db']
